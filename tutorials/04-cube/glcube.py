# Author: Kaan Eraslan
# purpose draw a rectangle on window

import numpy as np
import os
import sys
import ctypes
from camera import QtCamera
from utils import computePerspectiveNp
from utils import computePerspectiveQt
from utils import arr2qmat

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

        # camera
        self.camera = QtCamera()

        # shaders etc
        cubeTutoDir = os.path.dirname(__file__)
        shaderDir = os.path.join(cubeTutoDir, "shaders")
        availableShaders = ["cube", "light"]
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
        self.lightVao = QOpenGLVertexArrayObject()
        self.program = QOpenGLShaderProgram()
        self.lightProgram = QOpenGLShaderProgram()

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

    def useShaderSingleName(
        self,
        shaderProgram: QOpenGLShaderProgram,
        shaderName: str,
        attrLocs: dict
    ):
        "Use shader name"
        # creating shader program
        shaderProgram = QOpenGLShaderProgram(self.context)
        vshader = self.loadVertexShader(shaderName)
        fshader = self.loadFragmentShader(shaderName)

        shaderProgram.addShader(vshader)  # adding vertex shader
        shaderProgram.addShader(fshader)  # adding fragment shader

        # bind attribute to a location
        self.bindLinkProgram(
            shaderProgram,
            attrLocs)

    def bindLinkProgram(self,
                        shaderProgram,
                        attrLocs: dict):
        "bind attributes to program and link"
        self.bindAttributeLocations(
            shaderProgram,
            attrLocs
        )
        # link shader program
        isLinked = shaderProgram.link()
        print("shader program is linked: ",
              isLinked)
        # bind the program
        shaderProgram.bind()

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

    def setUniformValues(self,
                         uniformVal: dict,
                         shaderProgram):
        "Set uniform values"
        print("shader linked:",
              shaderProgram.isLinked())
        print("shader program", shaderProgram)
        print("program shaders:", shaderProgram.shaders())
        for key, val in uniformVal.items():
            print("key: ", key)
            uniLoc = shaderProgram.uniformLocation(key)
            shaderProgram.setUniformValue(uniLoc, val)

    def bindAttributeLocations(self,
                               shaderProgram,
                               attrLocs: dict):
        "bind attributes to locations"
        for name, location in attrLocs.items():
            shaderProgram.bindAttributeLocation(
                name, location
            )

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
        funcs.glClearColor(0.0, 0.0, 0, 0)
        funcs.glEnable(pygl.GL_DEPTH_TEST)

        # create uniform values for shaders
        lightPos = QVector3D(0.2, 1.0, 0.5)
        projectionMatrix = QMatrix4x4(*[0.0 for i in range(16)])
        projectionMatrix.perspective(
            self.camera.zoom,
            self.width() / self.height(),
            0.2, 100.0)

        viewMatrix = self.camera.getViewMatrix()

        # models
        cubeModel = QMatrix4x4()

        objColor = QVector3D(1.0, 0.5, 0.3)
        lightColor = QVector3D(1.0, 1.0, 1.0)

        uniformValues4CubeShader = {
            "view": viewMatrix,
            "projection": projectionMatrix,
            "model": cubeModel,
            "objectColor": objColor,
            "lightColor": lightColor,
        }
        #
        lampModel = QMatrix4x4()
        lampModel.translate(lightPos)
        lampModel.scale(
            QVector3D(0.2, 0.2, 0.2)
        )
        uniformValues4LightShader = {
            "view": viewMatrix,
            "projection": projectionMatrix,
            "model": lampModel,
        }

        # deal with shaders

        # cube shader
        self.program = QOpenGLShaderProgram(
            self.context
        )
        vshader = self.loadVertexShader("cube")
        fshader = self.loadFragmentShader("cube")
        self.program.addShader(vshader)  # adding vertex shader
        self.program.addShader(fshader)  # adding fragment shader
        attrsLocation = {"aPos": 0}
        self.program.bindAttributeLocation(
            "aPos", 0)

        isLinked = self.program.link()
        print("cube shader program is linked: ",
              isLinked)
        # bind the program
        self.program.bind()

        # set uniform values to cube shader
        viewLoc = self.program.uniformLocation("view")
        self.program.setUniformValue(viewLoc,
                                     viewMatrix)
        #
        projLoc = self.program.uniformLocation(
            "projection")
        self.program.setUniformValue(
            projLoc,
            projectionMatrix)
        #
        modelLoc = self.program.uniformLocation(
            "model")
        self.program.setUniformValue(modelLoc,
                                     cubeModel)
        #
        objLoc = self.program.uniformLocation(
            "objectColor")
        self.program.setUniformValue(objLoc,
                                     objColor)

        lightLoc = self.program.uniformLocation(
            "lightColor")
        self.program.setUniformValue(lightLoc,
                                     lightColor)

        # lamp shader
        self.lightProgram = QOpenGLShaderProgram(
            self.context)
        vshader = self.loadVertexShader("cube")
        fshader = self.loadFragmentShader("light")
        self.lightProgram.addShader(vshader)  # adding vertex shader
        self.lightProgram.addShader(fshader)  # adding fragment shader
        self.lightProgram.bindAttributeLocation(
            "aPos", 0)
        isLinked = self.lightProgram.link()
        print("light shader program is linked: ",
              isLinked)
        # bind the program
        self.lightProgram.bind()

        # set uniform values to light shader
        viewLoc = self.lightProgram.uniformLocation("view")
        self.lightProgram.setUniformValue(viewLoc,
                                          viewMatrix)
        #
        projLoc = self.lightProgram.uniformLocation(
            "projection")
        self.lightProgram.setUniformValue(
            projLoc,
            projectionMatrix)
        #
        modelLoc = self.lightProgram.uniformLocation(
            "model")
        self.lightProgram.setUniformValue(modelLoc,
                                          lampModel)

        # deal with vaos and vbo
        # create vao, lightVao, and vbo

        # vao
        isVao = self.vao.create()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)

        # vbo
        isVbo = self.vbo.create()
        isVboBound = self.vbo.bind()

        # check if vao and vbo are created
        print('vao created: ', isVao)
        print('vbo created: ', isVbo)

        # check if all are bound
        print("vbo bound: ", isVboBound)

        floatSize = ctypes.sizeof(ctypes.c_float)

        # allocate space on vbo buffer
        self.vbo.allocate(self.vertexData.tobytes(),
                          floatSize * self.vertexData.size)

        # dealing vertex attributes
        # cube object
        funcs.glEnableVertexAttribArray(0)
        nullptr = VoidPtr(0)
        funcs.glVertexAttribPointer(
            0,
            3,
            int(pygl.GL_FLOAT),
            int(pygl.GL_FALSE),
            3 * floatSize,
            nullptr
        )
        vaoBinder = None
        self.vbo.release()
        # light vao
        # lightVao holding light object
        isLightVao = self.lightVao.create()
        print('is light vao created: ', isLightVao)

        lightVaoBinder = QOpenGLVertexArrayObject.Binder(
            self.lightVao
        )
        print("light vao bound: ", lightVaoBinder)

        funcs.glEnableVertexAttribArray(0)
        funcs.glVertexAttribPointer(
            0,
            3,
            int(pygl.GL_FLOAT),
            int(pygl.GL_FALSE),
            3 * floatSize,
            nullptr)

    def paintGL(self):
        "drawing loop"
        funcs = self.context.functions()

        # clean up what was drawn
        funcs.glClear(pygl.GL_COLOR_BUFFER_BIT | pygl.GL_DEPTH_BUFFER_BIT)

        # actual drawing
        self.program.bind()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)

        funcs.glDrawArrays(
            pygl.GL_TRIANGLES,  # mode
            0,  # count
            36
        )
        vaoBinder = None

        self.lightProgram.bind()
        lightVaoBinder = QOpenGLVertexArrayObject.Binder(
            self.lightVao
        )
        funcs.glDrawArrays(
            pygl.GL_TRIANGLES,  # mode
            0,  # count
            36
        )
        self.lightProgram.release()
        lightVaoBinder = None
