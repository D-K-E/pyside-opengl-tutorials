# Author: Kaan Eraslan
# purpose interactive widget

import numpy as np
import os
import sys
import ctypes
from tutorials.utils.camera import QtCamera
from tutorials.utils.utils import computePerspectiveNp
from tutorials.utils.utils import computePerspectiveQt
from tutorials.utils.utils import arr2qmat

from PySide2.QtGui import QVector3D
from PySide2.QtGui import QImage
from PySide2.QtGui import QOpenGLVertexArrayObject
from PySide2.QtGui import QOpenGLBuffer
from PySide2.QtGui import QOpenGLShaderProgram
from PySide2.QtGui import QOpenGLShader
from PySide2.QtGui import QOpenGLContext
from PySide2.QtGui import QOpenGLTexture
from PySide2.QtGui import QMatrix4x4
from PySide2.QtGui import QVector4D
from PySide2.QtGui import QColor

from PySide2.QtWidgets import QApplication
from PySide2.QtWidgets import QMessageBox
from PySide2.QtWidgets import QOpenGLWidget

from PySide2.QtCore import QCoreApplication

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


class EventsGL(QOpenGLWidget):
    "Cube gl widget"

    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)

        # camera
        self.camera = QtCamera()
        self.camera.position = QVector3D(0.0, 0.0, 3.0)
        self.camera.front = QVector3D(0.0, 0.0, -1.0)
        self.camera.up = QVector3D(0.0, 1.0, 0.0)
        self.camera.movementSensitivity = 0.05

        # shaders etc
        tutoTutoDir = os.path.dirname(__file__)
        tutoPardir = os.path.join(tutoTutoDir, os.pardir)
        tutoPardir = os.path.realpath(tutoPardir)
        mediaDir = os.path.join(tutoPardir, "media")
        shaderDir = os.path.join(mediaDir, "shaders")

        availableShaders = ["cube"]
        self.shaders = {
            name: {
                "fragment": os.path.join(shaderDir, name + ".frag"),
                "vertex": os.path.join(shaderDir, name + ".vert")
            } for name in availableShaders
        }
        self.core = "--coreprofile" in QCoreApplication.arguments()
        imdir = os.path.join(mediaDir, "images")
        imFName = "im"
        imageFile1 = os.path.join(imdir, imFName + "0.png")
        self.image1 = QImage(imageFile1).mirrored()
        imageFile2 = os.path.join(imdir, imFName + "1.png")
        self.image2 = QImage(imageFile2).mirrored()

        # opengl data related
        self.context = QOpenGLContext()
        self.vao = QOpenGLVertexArrayObject()
        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.program = QOpenGLShaderProgram()
        self.texture1 = None
        self.texture2 = None
        self.texUnit1 = 0
        self.texUnit2 = 1

        # vertex data
        self.cubeVertices = np.array([
            # pos vec3 || texcoord vec2
            -0.5, -0.5, -0.5, 0.0, 0.0,
            0.5, -0.5, -0.5, 1.0, 0.0,
            0.5,  0.5, -0.5,  1.0, 1.0,
            0.5,  0.5, -0.5,  1.0, 1.0,
            -0.5,  0.5, -0.5,  0.0, 1.0,
            -0.5, -0.5, -0.5,  0.0, 0.0,

            -0.5, -0.5,  0.5,  0.0, 0.0,
            0.5, -0.5,  0.5,  1.0, 0.0,
            0.5,  0.5,  0.5,  1.0, 1.0,
            0.5,  0.5,  0.5,  1.0, 1.0,
            -0.5,  0.5,  0.5,  0.0, 1.0,
            -0.5, -0.5,  0.5,  0.0, 0.0,

            -0.5,  0.5,  0.5,  1.0, 0.0,
            -0.5,  0.5, -0.5,  1.0, 1.0,
            -0.5, -0.5, -0.5,  0.0, 1.0,
            -0.5, -0.5, -0.5,  0.0, 1.0,
            -0.5, -0.5,  0.5,  0.0, 0.0,
            -0.5,  0.5,  0.5,  1.0, 0.0,

            0.5,  0.5,  0.5,  1.0, 0.0,
            0.5,  0.5, -0.5,  1.0, 1.0,
            0.5, -0.5, -0.5,  0.0, 1.0,
            0.5, -0.5, -0.5,  0.0, 1.0,
            0.5, -0.5,  0.5,  0.0, 0.0,
            0.5,  0.5,  0.5,  1.0, 0.0,

            -0.5, -0.5, -0.5,  0.0, 1.0,
            0.5, -0.5, -0.5,  1.0, 1.0,
            0.5, -0.5,  0.5,  1.0, 0.0,
            0.5, -0.5,  0.5,  1.0, 0.0,
            -0.5, -0.5,  0.5,  0.0, 0.0,
            -0.5, -0.5, -0.5,  0.0, 1.0,

            -0.5,  0.5, -0.5,  0.0, 1.0,
            0.5,  0.5, -0.5,  1.0, 1.0,
            0.5,  0.5,  0.5,  1.0, 0.0,
            0.5,  0.5,  0.5,  1.0, 0.0,
            -0.5,  0.5,  0.5,  0.0, 0.0,
            -0.5,  0.5, -0.5,  0.0, 1.0
        ], dtype=ctypes.c_float
        )
        # cube worldSpace coordinates
        self.cubeCoords = [
            QVector3D(0.2,  1.1,  -1.0),
            QVector3D(2.0,  5.0, -15.0),
            QVector3D(-1.5, -2.2, -2.5),
            QVector3D(-3.8, -2.0, -12.3),
            QVector3D(2.4, -0.4, -3.5),
            QVector3D(-1.7,  3.0, -7.5),
            QVector3D(1.3, -2.0, -2.5),
            QVector3D(1.5,  2.0, -2.5),
            QVector3D(1.5,  0.2, -1.5),
            QVector3D(-1.3,  1.0, -1.5)
        ]
        self.rotateVector = QVector3D(0.7, 0.2, 0.5)

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

    def useShaders(
        self,
        shaderProgram: QOpenGLShaderProgram,
        shaders: {"shaderName": ["shaderType"]},
        attrLocs: dict
    ):
        ""
        print("program shaders: ",
              shaderProgram.shaders())
        for shaderName, shaderTypes in shaders.items():
            #
            if len(shaderTypes) == 2:
                self.useShaderSingleName(
                    shaderProgram=shaderProgram,
                    shaderName=shaderName,
                    attrLocs=attrLocs
                )
            elif len(shaderTypes) == 1:
                shaderType = shaderTypes[0]
                if shaderType == "vertex":
                    shader = self.loadVertexShader(
                        shaderName)
                else:
                    shader = self.loadFragmentShader(
                        shaderName
                    )

                shaderProgram.addShader(shader)
                # adding shader
                self.bindLinkProgram(
                    shaderProgram,
                    attrLocs)

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

    def moveCamera(self, direction: str):
        "Move camera to certain direction and update gl widget"
        self.camera.move(direction, deltaTime=0.05)
        self.update()

    def turnAround(self, x: float, y: float):
        ""
        self.camera.lookAround(xoffset=x,
                               yoffset=y,
                               pitchBound=True)
        self.update()

    def rotateCubes(self, xval: float,
                    yval: float, zval: float):
        ""
        self.rotateVector.setZ(zval)
        self.rotateVector.setY(yval)
        self.rotateVector.setX(xval)
        self.update()

    def cleanUpGl(self):
        "Clean up everything"
        self.context.makeCurrent()
        self.vbo.destroy()
        self.texture1.destroy()
        self.texture2.destroy()
        self.vao.destroy()
        del self.program
        self.program = None
        self.doneCurrent()

    def resizeGL(self, width: int, height: int):
        "Resize the viewport"
        funcs = self.context.functions()
        funcs.glViewport(0, 0, width, height)

    def initializeGL(self):
        print('gl initial')
        print(self.getGlInfo())

        # create context and make it current
        self.context.create()
        self.context.aboutToBeDestroyed.connect(
            self.cleanUpGl)

        # initialize functions
        funcs = self.context.functions()
        funcs.initializeOpenGLFunctions()
        funcs.glClearColor(0.0, 0.4, 0.4, 0)
        funcs.glEnable(pygl.GL_DEPTH_TEST)
        funcs.glEnable(pygl.GL_TEXTURE_2D)

        # create uniform values for shaders
        # deal with shaders

        # cube shader
        self.program = QOpenGLShaderProgram(
            self.context
        )
        vshader = self.loadVertexShader("cube")
        fshader = self.loadFragmentShader("cube")
        self.program.addShader(vshader)  # adding vertex shader
        self.program.addShader(fshader)  # adding fragment shader
        self.program.bindAttributeLocation(
            "aPos", 0)
        self.program.bindAttributeLocation(
            "aTexCoord", 1)

        isLinked = self.program.link()
        print("cube shader program is linked: ",
              isLinked)
        # bind the program
        self.program.bind()

        self.program.setUniformValue('myTexture1', self.texUnit1)
        self.program.setUniformValue('myTexture2', self.texUnit2)
        #
        # deal with vaos and vbo
        # vbo
        isVbo = self.vbo.create()
        isVboBound = self.vbo.bind()

        floatSize = ctypes.sizeof(ctypes.c_float)

        # allocate space on vbo buffer
        self.vbo.allocate(
            self.cubeVertices.tobytes(),
            floatSize * self.cubeVertices.size)
        self.vao.create()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)
        funcs.glEnableVertexAttribArray(0)  # viewport
        funcs.glVertexAttribPointer(0,
                                    3,
                                    int(pygl.GL_FLOAT),
                                    int(pygl.GL_FALSE),
                                    5 * floatSize,
                                    VoidPtr(0)
                                    )
        funcs.glEnableVertexAttribArray(1)
        funcs.glVertexAttribPointer(1,
                                    2,
                                    int(pygl.GL_FLOAT),
                                    int(pygl.GL_FALSE),
                                    5 * floatSize,
                                    VoidPtr(3 * floatSize)
                                    )
        # deal with textures
        # first texture
        self.texture1 = QOpenGLTexture(
            QOpenGLTexture.Target2D)
        self.texture1.create()
        self.texture1.bind(self.texUnit1)
        self.texture1.setData(self.image1)
        self.texture1.setMinMagFilters(
            QOpenGLTexture.Nearest,
            QOpenGLTexture.Nearest)
        self.texture1.setWrapMode(
            QOpenGLTexture.DirectionS,
            QOpenGLTexture.Repeat)
        self.texture1.setWrapMode(
            QOpenGLTexture.DirectionT,
            QOpenGLTexture.Repeat)

        # second texture
        self.texture2 = QOpenGLTexture(
            QOpenGLTexture.Target2D)
        self.texture2.create()
        self.texture2.bind(self.texUnit2)
        self.texture2.setData(self.image2)
        self.texture2.setMinMagFilters(
            QOpenGLTexture.Linear,
            QOpenGLTexture.Linear)
        self.texture2.setWrapMode(
            QOpenGLTexture.DirectionS,
            QOpenGLTexture.Repeat)
        self.texture2.setWrapMode(
            QOpenGLTexture.DirectionT,
            QOpenGLTexture.Repeat)

        self.vbo.release()
        vaoBinder = None
        print("gl initialized")

    def paintGL(self):
        "drawing loop"
        funcs = self.context.functions()

        # clean up what was drawn
        funcs.glClear(
            pygl.GL_COLOR_BUFFER_BIT | pygl.GL_DEPTH_BUFFER_BIT
        )
        self.vao.bind()
        self.vbo.bind()

        # actual drawing
        self.program.bind()
        # set projection matrix
        projectionMatrix = QMatrix4x4()
        projectionMatrix.perspective(
            self.camera.zoom,
            self.width() / self.height(),
            0.2, 100.0)

        self.program.setUniformValue('projection',
                                     projectionMatrix)

        # set view/camera matrix
        viewMatrix = self.camera.getViewMatrix()
        self.program.setUniformValue('view',
                                     viewMatrix)

        # bind textures
        for i, pos in enumerate(self.cubeCoords):
            #
            cubeModel = QMatrix4x4()
            cubeModel.translate(pos)
            angle = 30 * i
            cubeModel.rotate(angle, self.rotateVector)
            self.program.setUniformValue("model",
                                         cubeModel)
            self.texture1.bind(self.texUnit1)
            self.texture2.bind(self.texUnit2)
            funcs.glDrawArrays(
                pygl.GL_TRIANGLES,
                0,
                36
            )
        self.vbo.release()
        self.program.release()
        self.texture1.release()
        self.texture2.release()