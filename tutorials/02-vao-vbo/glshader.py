# Author: Kaan Eraslan

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


class TriangleGL(QOpenGLWidget):
    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)

        # shaders etc
        triangleTutoDir = os.path.dirname(__file__)
        shaderDir = os.path.join(triangleTutoDir, "shaders")
        availableShaders = ["triangle", "triangle2"]
        self.shaders = {
            name: {
                "fragment": os.path.join(shaderDir, name + ".frag"),
                "vertex": os.path.join(shaderDir, name + ".vert")
            } for name in availableShaders
        }
        self.core = "--coreprofile" in QCoreApplication.arguments()

        # opengl data related
        self.context = QOpenGLContext()
        self.vao1 = QOpenGLVertexArrayObject()
        self.vbo1 = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.vao2 = QOpenGLVertexArrayObject()
        self.vbo2 = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)

        self.program1 = QOpenGLShaderProgram()
        self.program2 = QOpenGLShaderProgram()

        # some vertex data for corners of triangle
        self.vertexData1 = np.array(
            [0.9, 0.9, 0.0,  # x, y, z
             0.9, 0.7, 0.0,  # x, y, z
             0.7, 0.9, 0.0],  # x, y, z
            dtype=ctypes.c_float
        )
        self.vertexData2 = np.array(
            [-0.9, -0.9, 0.0,  # x, y, z
             -0.9, -0.7, 0.0,  # x, y, z
             -0.7, -0.9, 0.0],  # x, y, z
            dtype=ctypes.c_float
        )
        # triangle color
        self.triangleColor1 = QVector4D(1.0, 0.0, 0.0, 0.0)  # yellow triangle
        self.triangleColor2 = QVector4D(
            0.0, 0.0, 0.5, 0.0)  # not yellow triangle

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

    def initializeGL(self):
        print('gl initial')
        print(self.getGlInfo())
        # create context and make it current
        self.context.create()
        self.context.aboutToBeDestroyed.connect(self.cleanUpGl)

        # initialize functions
        funcs = self.context.functions()
        funcs.initializeOpenGLFunctions()
        funcs.glClearColor(1, 1, 1, 1)

        # deal with shaders
        # first shader
        shaderName = "triangle"
        vshader = self.loadVertexShader(shaderName)
        fshader = self.loadFragmentShader(shaderName)

        # creating shader program
        self.program1 = QOpenGLShaderProgram(self.context)
        self.program1.addShader(vshader)  # adding vertex shader
        self.program1.addShader(fshader)  # adding fragment shader

        # bind attribute to a location
        self.program1.bindAttributeLocation("aPos", 0)

        # link shader program1
        isLinked = self.program1.link()
        print("shader program1 is linked: ", isLinked)

        # bind the program1
        self.program1.bind()

        # specify uniform value
        colorLoc = self.program1.uniformLocation("color")
        self.program1.setUniformValue(colorLoc,
                                     self.triangleColor1)

        # second shader
        shaderName = "triangle2"
        vshader = self.loadVertexShader(shaderName)
        fshader = self.loadFragmentShader(shaderName)

        #
        self.program2 = QOpenGLShaderProgram(self.context)
        self.program2.addShader(vshader)  # adding vertex shader
        self.program2.addShader(fshader)  # adding fragment shader

        # bind attribute to a location
        self.program2.bindAttributeLocation("aPos", 0)

        # link shader program2
        isLinked = self.program2.link()
        print("shader program2 is linked: ", isLinked)

        # bind the program2
        self.program2.bind()

        # specify uniform value
        colorLoc = self.program2.uniformLocation("color")
        self.program2.setUniformValue(colorLoc,
                                     self.triangleColor2)

        # self.useShader("triangle")

        # deal with vao and vbo

        # create vao and vbo

        # vao
        isVao = self.vao1.create()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao1)

        # vbo
        isVbo = self.vbo1.create()
        isBound = self.vbo1.bind()

        # check if vao and vbo are created
        print('vao created: ', isVao)
        print('vbo created: ', isVbo)

        floatSize = ctypes.sizeof(ctypes.c_float)

        # allocate space on buffer
        self.vbo1.allocate(self.vertexData1.tobytes(),
                           floatSize * self.vertexData1.size)
        funcs.glEnableVertexAttribArray(0)
        nullptr = VoidPtr(0)
        funcs.glVertexAttribPointer(0,
                                    3,
                                    int(pygl.GL_FLOAT),
                                    int(pygl.GL_FALSE),
                                    3 * floatSize,
                                    nullptr)
        self.vbo1.release()
        vaoBinder = None

        # second triangle vao vbo
        # vao
        isVao = self.vao2.create()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao2)

        # vbo
        isVbo = self.vbo2.create()
        isBound = self.vbo2.bind()

        # check if vao and vbo are created
        print('vao created: ', isVao)
        print('vbo created: ', isVbo)

        floatSize = ctypes.sizeof(ctypes.c_float)

        # allocate space on buffer
        self.vbo2.allocate(self.vertexData2.tobytes(),
                           floatSize * self.vertexData2.size)
        funcs.glEnableVertexAttribArray(0)
        nullptr = VoidPtr(0)
        funcs.glVertexAttribPointer(0,
                                    3,
                                    int(pygl.GL_FLOAT),
                                    int(pygl.GL_FALSE),
                                    3 * floatSize,
                                    nullptr)
        self.vbo2.release()
        self.program2.release()

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
        funcs.glClear(pygl.GL_COLOR_BUFFER_BIT)

        # actual drawing
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao1)
        self.program1.bind()
        funcs.glDrawArrays(pygl.GL_TRIANGLES,  # mode
                           0,  # first
                           3)  # count
        vaoBinder = None
        self.program1.release()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao2)
        self.program2.bind()
        funcs.glDrawArrays(pygl.GL_TRIANGLES,  # mode
                           0,  # first
                           3)  # count
        vaoBinder = None
        self.program2.release()

