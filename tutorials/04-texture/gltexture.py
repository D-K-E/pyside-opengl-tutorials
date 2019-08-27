# author: Kaan Eraslan

import numpy as np
from PIL import Image
import os
import sys
import ctypes

from PySide2.QtGui import QImage
from PySide2.QtGui import QOpenGLVertexArrayObject
from PySide2.QtGui import QOpenGLBuffer
from PySide2.QtGui import QOpenGLShaderProgram
from PySide2.QtGui import QOpenGLShader
from PySide2.QtGui import QOpenGLTexture
from PySide2.QtGui import QOpenGLContext

from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QMessageBox
from PySide2.QtWidgets import QOpenGLWidget

from PySide2.QtCore import QCoreApplication
from PySide2.QtCore import Qt

from PySide2.shiboken2 import VoidPtr


try:
    from OpenGL import GL as pygl
except ImportError:
    app = QApplication(sys.argv)
    messageBox = QMessageBox(QMessageBox.Critical, "OpenGL hellogl",
                             "PyOpenGL must be installed to run this example.",
                             QMessageBox.Close)
    messageBox.setDetailedText(
        "Run:\npip install PyOpenGL PyOpenGL_accelerate")
    messageBox.exec_()
    sys.exit(1)


class TextureGL(QOpenGLWidget):
    "Texture loading opengl widget"

    def __init__(self, parent=None):
        "Constructor"
        QOpenGLWidget.__init__(self, parent)
        tutoTutoDir = os.path.dirname(__file__)
        tutoPardir = os.path.join(tutoTutoDir, os.pardir)
        tutoPardir = os.path.realpath(tutoPardir)
        mediaDir = os.path.join(tutoPardir, "media")
        shaderDir = os.path.join(mediaDir, "shaders")
        #
        availableShaders = ["texture"]
        self.shaders = {
            name: {
                "fragment": os.path.join(shaderDir, name + ".frag"),
                "vertex": os.path.join(shaderDir, name + ".vert")
            } for name in availableShaders
        }
        imdir = os.path.join(mediaDir, "images")
        imFName = "im"
        imageFile = os.path.join(imdir, imFName + "0.png")
        print("image file:", imageFile)
        self.imagefile = imageFile
        # self.image = QImage(imageFile).mirrored().scaledToWidth(self.width())
        self.image = QImage(imageFile).mirrored()
        self.imagepil = Image.open(imageFile)
        self.imagenp = np.array(self.imagepil)
        self.imagenp = self.imagenp.astype(ctypes.c_uint)
        print("image qimage:", self.image)
        self.core = "--coreprofile" in QCoreApplication.arguments()

        # opengl data related
        self.context = QOpenGLContext()
        self.program = QOpenGLShaderProgram()
        self.vao = QOpenGLVertexArrayObject()
        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.texture = None
        self.indices = np.array([
            0, 1, 3,  # first triangle
            1, 2, 3  # second triangle
        ], dtype=ctypes.c_uint)

        # vertex data of the panel that would hold the image
        self.vertexData = np.array([
            # viewport position || texture coords
            0.5,  0.5,  0.0, 1.0, 1.0,  # top right
            0.5,  -0.5, 0.0, 1.0, 0.0,  # bottom right
            -0.5, -0.5, 0.0, 0.0, 0.0,  # bottom left
            -0.5, 0.5,  0.0, 0.0, 1.0  # top left
        ], dtype=ctypes.c_float)

    def loadShader(self,
                   shaderName: str,
                   shaderType: str):
        "Load shader"
        shader = self.shaders[shaderName]
        shaderSourcePath = shader[shaderType]
        if shaderType == "vertex":
            shader = QOpenGLShader(QOpenGLShader.Vertex)
        else:
            shader = QOpenGLShader(QOpenGLShader.Fragment)
        #
        isCompiled = shader.compileSourceFile(shaderSourcePath)

        if isCompiled is False:
            print(shader.log())
            raise ValueError(
                "{0} shader {2} known as {1} is not compiled".format(
                    shaderType, shaderName, shaderSourcePath
                )
            )
        return shader

    def loadVertexShader(self, shaderName: str):
        "load vertex shader"
        return self.loadShader(shaderName, "vertex")

    def loadFragmentShader(self, shaderName: str):
        "load fragment shader"
        return self.loadShader(shaderName, "fragment")

    def getGlInfo(self):
        "Get opengl info"
        info = """
            Vendor: {0}
            Renderer: {1}
            OpenGL Version: {2}
            Shader Version: {3}
            """.format(
            pygl.glGetString(pygl.GL_VENDOR),
            pygl.glGetString(pygl.GL_RENDERER),
            pygl.glGetString(pygl.GL_VERSION),
            pygl.glGetString(pygl.GL_SHADING_LANGUAGE_VERSION)
        )
        return info

    def cleanUpGl(self):
        "Clean up everything"
        self.context.makeCurrent()
        del self.program
        self.program = None
        self.texture.release()
        self.doneCurrent()

    def resizeGL(self, width: int, height: int):
        "Resize the viewport"
        funcs = self.context.functions()
        funcs.glViewport(0, 0, width, height)

    def initializeGL(self):
        "Initialize opengl "
        print('gl initial')
        print(self.getGlInfo())
        # create context and make it current
        self.context.create()
        self.context.aboutToBeDestroyed.connect(self.cleanUpGl)

        # initialize functions
        funcs = self.context.functions()
        funcs.initializeOpenGLFunctions()
        funcs.glClearColor(1, 0, 1, 1)
        funcs.glEnable(pygl.GL_TEXTURE_2D)

        # shader
        shaderName = "texture"
        vshader = self.loadVertexShader(shaderName)
        fshader = self.loadFragmentShader(shaderName)

        # create shader program
        self.program = QOpenGLShaderProgram(self.context)
        self.program.addShader(vshader)
        self.program.addShader(fshader)

        # bind attribute location
        self.program.bindAttributeLocation("aPos", 0)
        self.program.bindAttributeLocation("aTexCoord", 1)

        # link shader program
        isLinked = self.program.link()
        print("shader program is linked: ", isLinked)

        # activate shader program to set uniform an attribute values
        self.program.bind()
        self.program.setUniformValue('myTexture', 0)

        # vbo
        isVbo = self.vbo.create()
        isVboBound = self.vbo.bind()

        floatSize = ctypes.sizeof(ctypes.c_float)

        # allocate vbo
        self.vbo.allocate(self.vertexData.tobytes(),
                          floatSize * self.vertexData.size)

        # texture new school
        self.texture = QOpenGLTexture(QOpenGLTexture.Target2D)
        isTexture = self.texture.create()
        textureID = self.texture.textureId()
        print("tex id: ", textureID)
        # new school
        self.texture.bind()
        self.texture.setData(self.image)
        self.texture.setMinMagFilters(QOpenGLTexture.Linear,
                                      QOpenGLTexture.Linear)
        self.texture.setWrapMode(QOpenGLTexture.DirectionS,
                                 QOpenGLTexture.ClampToEdge)
        self.texture.setWrapMode(QOpenGLTexture.DirectionT,
                                 QOpenGLTexture.ClampToEdge)
        
        print("texture created: ", isTexture)

    def paintGL(self):
        "paint gl"
        funcs = self.context.functions()
        # clean up what was drawn
        funcs.glClear(pygl.GL_COLOR_BUFFER_BIT)

        self.program.bind()
        self.program.enableAttributeArray(0)
        self.program.enableAttributeArray(1)
        floatSize = ctypes.sizeof(ctypes.c_float)

        # set attribute values
        self.program.setAttributeBuffer(0,  # viewport position
                                        pygl.GL_FLOAT,  # coord type
                                        0,  # offset
                                        3,
                                        5 * floatSize
                                        )
        self.program.setAttributeBuffer(1,  # viewport position
                                        pygl.GL_FLOAT,  # coord type
                                        3 * floatSize,  # offset
                                        2,
                                        5 * floatSize
                                        )
        # bind texture
        self.texture.bind()
        funcs.glDrawElements(pygl.GL_TRIANGLES,
                             self.indices.size, pygl.GL_UNSIGNED_INT,
                             self.indices.tobytes())
        # funcs.glDrawArrays(pygl.GL_TRIANGLES, 0, 6)
