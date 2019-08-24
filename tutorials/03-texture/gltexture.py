# author: Kaan Eraslan

import numpy as np
import os
import sys
import ctypes

from PySide2 import QtWidgets, QtCore, QtGui
from PySide2.QtGui import QVector3D
from PySide2.QtGui import QOpenGLVertexArrayObject
from PySide2.QtGui import QOpenGLBuffer
from PySide2.QtGui import QOpenGLShaderProgram
from PySide2.QtGui import QOpenGLShader
from PySide2.QtGui import QOpenGLContext
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


class TextureGL(QOpenGLWidget):
    "Texture loading opengl widget"

    def __init__(self, parent=None):
        ""
        QOpenGLWidget.__init__(self, parent)

        # media and project structure
        projectdir = os.getcwd()
        projectdir = os.path.join(projectdir, "qtopengl")
        assetsdir = os.path.join(projectdir, "assets")
        self.imagesdir = os.path.join(assetsdir, 'images')
        self.shadersdir = os.path.join(assetsdir, 'shaders')
        self.availableShaders = [
            "basic_color",
            "simpleLamp",
            "triangle",
            "portableTriangle",
            "portableTexture"
        ]
        self.shaders = {
            name: {"vertex": os.path.join(self.shadersdir, name + ".vert"),
                   "fragment": os.path.join(self.shadersdir, name + ".vert")}
            for name in self.availableShaders
        }

        self.core = "--coreprofile" in QCoreApplication.arguments()

        # opengl data related
        self.context = QOpenGLContext()
        self.vao = QOpenGLVertexArrayObject()
        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.ebo = QOpenGLBuffer(QOpenGLBuffer.IndexBuffer)
        self.program = QOpenGLShaderProgram()

        # shader uniform attribute related
        self.projectionMatrix = QMatrix4x4()
        self.cameraMatrix = QMatrix4x4()
        self.worldMatrix = QMatrix4x4()

        # locations of the attributes and uniforms
        self.projectionMatrixLoc = 0
        self.cameraMatrixLoc = 0
        self.normalMatrixLoc = 0
        self.lightPositionLoc = 0

        # some vertex data for corners of rectangle that would contain texture

        self.vertexData = np.array([  # viewport position xyz | colors xyz | texture coordinates xy
            0.5, 0.5, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0,  # top right
            0.5,  -0.5, 0.0, 0.0, 1.0, 0.0, 1.0, 0.0,  # bottom right
            -0.5, -0.5, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0,  # bottom let
            -0.5, 0.5,  0.0, 1.0, 1.0, 0.0, 0.0, 1.0  # top let
        ],
            dtype=ctypes.c_float
        )

    def loadShader(self,
                   shaderName: str,
                   shaderType: str):
        "Load shader"
        shader = self.shaders[shaderName]
        shaderpath = shader[shaderType]
        if shaderType == "vertex":
            shader = QOpenGLShader(QOpenGLShader.Vertex)
        else:
            shader = QOpenGLShader(QOpenGLShader.Fragment)
        #
        isCompiled = shader.compileSourceFile(shaderpath)

        if isCompiled is False:
            print(shader.log())
            raise ValueError(
                "{0} shader {1} in {2} is not compiled".format(
                    shaderType, shaderName, shaderpath
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

    def initializeGL(self):
        print('gl initial')
        print(self.getGlInfo())
        # create context and make it current
        self.context.create()
        # surface = QSurface(QSurface.OpenGLSurface)
        # self.context.makeCurrent(surface)
        self.context.aboutToBeDestroyed.connect(self.cleanUpGl)
        funcs = self.context.functions()
        funcs.initializeOpenGLFunctions()
        funcs.glClearColor(1, 1, 1, 1)

        # deal with shaders
        shaderName = "portableTriangle"
        vshader = self.loadVertexShader(shaderName)
        fshader = self.loadFragmentShader(shaderName)

        # creating shader program
        self.program = QOpenGLShaderProgram(self.context)
        self.program.addShader(vshader)  # adding vertex shader
        self.program.addShader(fshader)  # adding fragment shader

        # bind attribute to a location
        attrLocations = {"aPos": 0,
                         "aColor": 1,
                         "aTexCoord": 2}
        self.bindAttributes2ShaderProgram(attrLocations)

        # link shader program
        isLinked = self.program.link()
        print("shader program is linked: ", isLinked)

        # bind the program
        self.program.bind()

        # rectangle indices
        indices = np.array([0, 1, 3, 1, 2, 3], dtype=ctypes.c_float)

        # create vao, vbo and ebo
        # vao
        isVao = self.vao.create()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)

        # vbo
        isVbo = self.vbo.create()
        isVboBound = self.vbo.bind()

        # ebo
        isEbo = self.ebo.create()
        isEboBound = self.ebo.bind()

        # check if vao, vbo, ebo are created
        print('vao created: ', isVao)
        print('vbo created: ', isVbo)
        print('ebo created: ', isEbo)

        # check if they are bound
        print('vbo bound: ', isVboBound)
        print('ebo bound: ', isEboBound)

        floatSize = ctypes.sizeof(ctypes.c_float)
        nullptr = VoidPtr(0)

        # allocate space on vbo
        self.vbo.allocate(self.vertexData.tobytes(), # data,
                          floatSize * self.vertexData.size)

        # allocate space on ebo
        self.ebo.allocate(indices.tobytes(), indices.size * floatSize)

        # let's specify the attributes and point them

        # position attribute
        funcs.glEnableVertexAttribArray(attrLocations['aPos'])
        funcs.glVertexAttribPointer(attrLocations['aPos'], # location
                                    3, # size of attribute 3 for vec3
                                    int(pygl.GL_FLOAT),
                                    int(pygl.GL_FALSE),
                                    8 * floatSize,
                                    0)
        # color attribute
        funcs.glEnableVertexAttribArray(attrLocations['aColor'])
        funcs.glVertexAttribPointer(attrLocations['aColor'], # location
                                    3, # size of attribute 3 for vec3
                                    int(pygl.GL_FLOAT),
                                    int(pygl.GL_FALSE),
                                    8 * floatSize,
                                    3 * floatSize)
        # texture coordinate attribute
        funcs.glEnableVertexAttribArray(attrLocations['aTexCoord'])
        funcs.glVertexAttribPointer(attrLocations['aTexCoord'], # location
                                    2, # size of attribute 3 for vec2
                                    int(pygl.GL_FLOAT),
                                    int(pygl.GL_FALSE),
                                    8 * floatSize,  # offset
                                    6 * floatSize   # stride
                                    )





    def bindAttributes2ShaderProgram(self, attrLocations: dict):
        "Bind attributes to shader program"
        for attrName, location in attrLocations.items():
            self.program.bindAttributeLocation(attrName, location)
