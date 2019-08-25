# Author: Kaan Eraslan
# purpose draw a rectangle on window

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


class CubeGL(QOpenGLWidget):
    "Cube gl widget"

    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)

        # shaders etc
        cubeTutoDir = os.path.dirname(__file__)
        shaderDir = os.path.join(cubeTutoDir, "shaders")
        availableShaders = ["cube"]
        self.shaders = {
            name: {
                "fragment": os.path.join(shaderDir, name + ".frag"),
                "vertex": os.path.join(shaderDir, name + ".vert")
            } for name in availableShaders
        }
        self.core = "--coreprofile" in QCoreApplication.arguments()

        # opengl data related
        self.context = QOpenGLContext()
        self.vao = QOpenGLVertexArrayObject()
        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.program = QOpenGLShaderProgram()

        # vertex data
        self.vertexData = np.array([
            -0.5, -0.5, -0.5,
            0.5, -0.5, -0.5,
            0.5,  0.5, -0.5,
            0.5,  0.5, -0.5,
            -0.5,  0.5, -0.5,
            -0.5, -0.5, -0.5,

            -0.5, -0.5,  0.5,
            0.5, -0.5,  0.5,
            0.5,  0.5,  0.5,
            0.5,  0.5,  0.5,
            -0.5,  0.5,  0.5,
            -0.5, -0.5,  0.5,

            -0.5,  0.5,  0.5,
            -0.5,  0.5, -0.5,
            -0.5, -0.5, -0.5,
            -0.5, -0.5, -0.5,
            -0.5, -0.5,  0.5,
            -0.5,  0.5,  0.5,

            0.5,  0.5,  0.5,
            0.5,  0.5, -0.5,
            0.5, -0.5, -0.5,
            0.5, -0.5, -0.5,
            0.5, -0.5,  0.5,
            0.5,  0.5,  0.5,

            -0.5, -0.5, -0.5,
            0.5, -0.5, -0.5,
            0.5, -0.5,  0.5,
            0.5, -0.5,  0.5,
            -0.5, -0.5,  0.5,
            -0.5, -0.5, -0.5,

            -0.5,  0.5, -0.5,
            0.5,  0.5, -0.5,
            0.5,  0.5,  0.5,
            0.5,  0.5,  0.5,
            -0.5,  0.5,  0.5,
            -0.5,  0.5, -0.5,
        ],
            dtype=ctypes.c_float
        )
        # cube color
        self.cubeColor = QVector4D(0.0, 0.0, 0.0, 0.0)  # black cube
        # notice the correspondance the vec4 of fragment shader
        # and our choice here

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
        self.vbo.destroy()
        del self.program
        self.program = None
        self.doneCurrent()

    def resizeGL(self, width: int, height: int):
        "Resize the viewport"
        funcs = self.context.functions()
        funcs.glViewport(0, 0, width, height)

    def paintGL(self):
        "drawing loop"
        funcs = self.context.functions()

        # clean up what was drawn
        funcs.glClear(pygl.GL_COLOR_BUFFER_BIT | pygl.GL_DEPTH_BUFFER_BIT)

        # actual drawing
        self.program.bind()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)

        funcs.glDrawElements(pygl.GL_TRIANGLES,  # mode
                             6,  # count
                             pygl.GL_UNSIGNED_INT,  # type
                             self.vertexIndices.tobytes()  # indices
                             )

        self.program.release()
        vaoBinder = None

    def initializeGL(self):
        print('gl initial')
        print(self.getGlInfo())
        # create context and make it current
        self.context.create()
        self.context.aboutToBeDestroyed.connect(self.cleanUpGl)

        # initialize functions
        funcs = self.context.functions()
        funcs.initializeOpenGLFunctions()
        funcs.glClearColor(0.1, 0.4, 0, 0)
        funcs.glEnable(pygl.GL_DEPTH_TEST)

        # deal with shaders
        shaderName = "cube"
        vshader = self.loadVertexShader(shaderName)
        fshader = self.loadFragmentShader(shaderName)

        # creating shader program
        self.program = QOpenGLShaderProgram(self.context)
        self.program.addShader(vshader)  # adding vertex shader
        self.program.addShader(fshader)  # adding fragment shader

        # bind attribute to a location
        self.program.bindAttributeLocation("aPos", 0)

        # link shader program
        isLinked = self.program.link()
        print("shader program is linked: ", isLinked)

        # bind the program
        self.program.bind()

        # specify uniform values in shader program
        uniformVals = {
            "view": "",
            "model": "",
            "projection": "",
            "objectColor": QVector3D(1.0, 0.5, 0.3),
            "lightColor": QVector3D(1.0, 1.0, 1.0),
        }

        # Object Color
        objColorLoc = self.program.uniformLocation("objectColor")
        self.program.setUniformValue(colorLoc,
                                     self.rectangleColor)

        # self.useShader("triangle")

        # deal with vao and vbo

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

        # check if vao and vbo are created
        print('vao created: ', isVao)
        print('vbo created: ', isVbo)
        print('ebo created: ', isEbo)

        # check if all are bound
        print("vbo bound: ", isVboBound)
        print("ebo bound: ", isEboBound)

        floatSize = ctypes.sizeof(ctypes.c_float)
        uintSize = ctypes.sizeof(ctypes.c_uint)

        # allocate space on vbo buffer
        self.vbo.allocate(self.vertexData.tobytes(),
                          floatSize * self.vertexData.size)

        # allocate space on ebo buffer for index
        self.ebo.allocate(self.vertexIndices.tobytes(),
                          uintSize * self.vertexIndices.size)

        funcs.glEnableVertexAttribArray(0)
        nullptr = VoidPtr(0)
        funcs.glVertexAttribPointer(0,
                                    3,
                                    int(pygl.GL_FLOAT),
                                    int(pygl.GL_FALSE),
                                    3 * floatSize,
                                    nullptr)
        self.vbo.release()
        self.program.release()
        vaoBinder = None
