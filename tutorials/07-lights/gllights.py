# Author: Kaan Eraslan
# purpose interactive widget with lights

import numpy as np
import os
import sys
import ctypes
from tutorials.utils.camera import QtCamera
from tutorials.utils.light import QtShaderLight

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
from PySide2.QtCore import QRect

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


class LightsGL(QOpenGLWidget):
    "Cube gl widget"

    def __init__(self, parent=None):
        QOpenGLWidget.__init__(self, parent)

        # camera
        self.camera = QtCamera()
        self.camera.position = QVector3D(0.0, 0.0, 3.0)
        self.camera.front = QVector3D(0.0, 0.0, -1.0)
        self.camera.up = QVector3D(0.0, 1.0, 0.0)
        self.camera.movementSensitivity = 0.05

        # light source: point light source
        self.lamp = QtShaderLight()

        # shaders etc
        tutoTutoDir = os.path.dirname(__file__)
        tutoPardir = os.path.join(tutoTutoDir, os.pardir)
        tutoPardir = os.path.realpath(tutoPardir)
        mediaDir = os.path.join(tutoPardir, "media")
        shaderDir = os.path.join(mediaDir, "shaders")

        availableShaders = ["light", "lamp"]
        self.shaders = {
            name: {
                "fragment": os.path.join(shaderDir, name + ".frag"),
                "vertex": os.path.join(shaderDir, name + ".vert")
            } for name in availableShaders
        }
        self.core = "--coreprofile" in QCoreApplication.arguments()
        imdir = os.path.join(mediaDir, "images")
        imFName = "im"
        imageFile1 = os.path.join(imdir, imFName + "2.png")
        cropRect = QRect(0, 0, 500, 500)
        self.image1 = QImage(imageFile1).mirrored()
        normalMap = os.path.join(imdir, "nmap.png")
        self.nmap = QImage(normalMap)
        self.image1 = self.image1.copy(cropRect)
        self.nmap = self.nmap.copy(cropRect)
        self.shininess = 5.0

        # opengl data related
        self.context = QOpenGLContext()
        self.vao = QOpenGLVertexArrayObject()
        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.lampVao = QOpenGLVertexArrayObject()
        self.lampVbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.program = QOpenGLShaderProgram()
        self.lampProgram = QOpenGLShaderProgram()
        self.diffuseMap = None  # texture
        self.specularMap = None  # texture
        self.texUnit1 = 0
        self.texUnit2 = 1

        # vertex data
        self.cubeVertices = np.array([
            # pos vec3 || normal vec3 || texcoord vec2
            -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0,  0.0,
            0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  1.0,  0.0,
            0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0,  1.0,
            0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  1.0,  1.0,
            -0.5,  0.5, -0.5,  0.0,  0.0, -1.0,  0.0,  1.0,
            -0.5, -0.5, -0.5,  0.0,  0.0, -1.0,  0.0,  0.0,

            -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  0.0,  0.0,
            0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  1.0,  0.0,
            0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0,  1.0,
            0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  1.0,  1.0,
            -0.5,  0.5,  0.5,  0.0,  0.0,  1.0,  0.0,  1.0,
            -0.5, -0.5,  0.5,  0.0,  0.0,  1.0,  0.0,  0.0,

            -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0,  0.0,
            -0.5,  0.5, -0.5, -1.0,  0.0,  0.0,  1.0,  1.0,
            -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0,  1.0,
            -0.5, -0.5, -0.5, -1.0,  0.0,  0.0,  0.0,  1.0,
            -0.5, -0.5,  0.5, -1.0,  0.0,  0.0,  0.0,  0.0,
            -0.5,  0.5,  0.5, -1.0,  0.0,  0.0,  1.0,  0.0,

            0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0,  0.0,
            0.5,  0.5, -0.5,  1.0,  0.0,  0.0,  1.0,  1.0,
            0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0,  1.0,
            0.5, -0.5, -0.5,  1.0,  0.0,  0.0,  0.0,  1.0,
            0.5, -0.5,  0.5,  1.0,  0.0,  0.0,  0.0,  0.0,
            0.5,  0.5,  0.5,  1.0,  0.0,  0.0,  1.0,  0.0,

            -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0,  1.0,
            0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  1.0,  1.0,
            0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0,  0.0,
            0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  1.0,  0.0,
            -0.5, -0.5,  0.5,  0.0, -1.0,  0.0,  0.0,  0.0,
            -0.5, -0.5, -0.5,  0.0, -1.0,  0.0,  0.0,  1.0,

            -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0,  1.0,
            0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  1.0,  1.0,
            0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0,  0.0,
            0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  1.0,  0.0,
            -0.5,  0.5,  0.5,  0.0,  1.0,  0.0,  0.0,  0.0,
            -0.5,  0.5, -0.5,  0.0,  1.0,  0.0,  0.0,  1.0
        ], dtype=ctypes.c_float
        )
        self.lampVertices = np.array(
            [  # pos vec3 || texcoord vec2
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
            dtype=ctypes.c_float)
        # cube worldSpace coordinates
        self.cubeCoords = [
            QVector3D(0.0,  0.0,  -2.0),
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
        self.rotVectorCube = QVector3D(0.7, 0.2, 0.5)
        self.rotVectorLamp = QVector3D(0.1, 0.2, 0.5)
        self.rotationAngle = 45.0

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
        self.rotVectorCube.setZ(zval)
        self.rotVectorCube.setY(yval)
        self.rotVectorCube.setX(xval)
        self.update()

    def changeShininess(self, val: float):
        "set a new shininess value to cube fragment shader"
        self.shininess = val

    def setLightPos(self, xval: float,
                    yval: float, zval: float):
        ""
        newpos = QVector3D(xval, yval, zval)
        self.lamp.setPosition(vec=newpos)
        self.update()

    def rotateLight(self, xval: float,
                    yval: float, zval: float):
        ""
        newRotVec = QVector3D(xval, yval, zval)
        self.rotVectorLamp = newRotVec
        self.lamp.setDirection(vec=newRotVec)
        self.update()

    def changeLampIntensity(self,
                            channel: str,
                            val: float,
                            colorType="all"):
        ""
        availables = ["red", "green", "blue", "all"]
        if channel not in availables:
            mess = "Unknown channel name " + channel
            mess += ", available channels are: "
            mess += "red, green, blue, all"
            raise ValueError(mess)
        self.lamp.setIntensity(colorType=colorType,
                               channel=channel,
                               val=val)
        self.update()

    def changeLampIntensityCoefficient(self,
                                       channel: str,
                                       val: float,
                                       colorType="all"):
        ""
        availables = ["red", "green", "blue", "all"]
        if channel not in availables:
            mess = "Unknown channel name " + channel
            mess += ", available channels are: "
            mess += "red, green, blue, all"
            raise ValueError(mess)
        #
        self.lamp.setCoeffs(colorType=colorType,
                            channel=channel,
                            val=val)
        self.update()

    def changeAmbientLightIntensity(self, xval: float,
                                    yval: float, zval: float):
        ""
        self.lamp.ambient.setIntensity(vec=QVector3D(xval,
                                                     yval,
                                                     zval))
        self.update()

    def changeAmbientLightCoeffs(self, xval: float, yval: float,
                                 zval: float):
        self.lamp.ambient.setCoeffs(vec=QVector3D(xval, yval, zval))
        self.update()

    def setLampAttenuation(self,
                           attenConst: float,
                           attenLin: float,
                           attenQuad: float,
                           colorType="all",
                           ):
        "set linear attenuation"
        vec = QVector3D(attenConst, attenLin, attenQuad)
        self.lamp.setAttenuation(vec=vec,
                                 colorType=colorType)
        self.update()

    def setCutOff(self, val):
        self.lamp.setCutOff(val)
        self.update()

    def setRotationAngle(self,
                         val: float):
        self.rotationAngle = val
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

    def setCubeUniforms_proc(self):
        ""
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
        # end vertex shader
        # fragment shader
        self.program.setUniformValue("material.shininess",
                                     self.shininess)
        self.program.setUniformValue("light.position",
                                     self.lamp.position)
        self.program.setUniformValue("light.direction", self.lamp.direction)
        self.program.setUniformValue("light.ambient",
                                     self.lamp.ambient.intensity)
        self.program.setUniformValue("light.diffuse",
                                     self.lamp.diffuse.intensity)
        self.program.setUniformValue("light.specular",
                                     self.lamp.specular.intensity)
        self.program.setUniformValue("coeffs.ambient",
                                     self.lamp.ambient.getCoeffAverage())
        self.program.setUniformValue("coeffs.diffuse",
                                     self.lamp.diffuse.getCoeffAverage())
        self.program.setUniformValue("coeffs.specular",
                                     self.lamp.specular.getCoeffAverage())
        self.program.setUniformValue("coeffs.lightCutOff",
                                     self.lamp.cutOff)
        self.program.setUniformValue("coeffs.attrConstant",
                                     self.lamp.attenuation.x())
        self.program.setUniformValue("coeffs.attrLinear",
                                     self.lamp.attenuation.y())
        self.program.setUniformValue("coeffs.attrQuadratic",
                                     self.lamp.attenuation.z())
        self.program.setUniformValue("viewerPosition", self.camera.position)
        # end fragment shader
        return

    def setCubeModelUniform_proc(self, i: int, pos: QVector3D):
        "procedure for setting cube uniform"
        cubeModel = QMatrix4x4()
        cubeModel.translate(pos)
        angle = 30 * i
        cubeModel.rotate(angle, self.rotVectorCube)
        self.program.setUniformValue("model",
                                     cubeModel)
        self.texture1.bind(self.texUnit1)
        self.texture2.bind(self.texUnit2)
        return

    def setLampUniforms_proc(self):
        projectionMatrix = QMatrix4x4()
        projectionMatrix.perspective(
            self.camera.zoom,
            self.width() / self.height(),
            0.2, 100.0)
        viewMatrix = self.camera.getViewMatrix()
        self.lampProgram.setUniformValue("projection",
                                         projectionMatrix)
        self.lampProgram.setUniformValue("view", viewMatrix)
        lampModel = QMatrix4x4()
        lampModel.translate(self.lamp.position)
        lampModel.rotate(self.rotationAngle,
                         self.rotVectorLamp)
        self.lampProgram.setUniformValue("model",
                                         lampModel)
        self.lampProgram.setUniformValue(
            "color",
            self.lamp.diffuse.color
        )

    def lampShaderInit_proc(self, vshader, fshader):
        self.lampProgram.addShader(vshader)
        self.lampProgram.addShader(fshader)
        self.lampProgram.bindAttributeLocation(
            "aPos", 0)
        # lamp needs view, projection, model matrices
        # view would come from camera
        # model is cube
        # lamp also sets a position as attribute and a color as uniform
        # lamp vertices prepare for that
        isLinked = self.lampProgram.link()
        print("lamp program is linked: ", isLinked)
        # bind the lamp
        self.lampProgram.bind()

    def cubeShaderInit_proc(self, vshader, fshader, attrLocs):
        self.program.addShader(vshader)
        self.program.addShader(fshader)
        self.program.bindAttributeLocation(
            "aPos", 0)
        self.program.bindAttributeLocation(
            "aNormal", attrLocs['aNormal'])
        self.program.bindAttributeLocation(
            "aTexCoord", attrLocs['aTexCoord'])
        isLinked = self.program.link()
        print("light cube shader program is linked: ",
              isLinked)
        # bind the program
        self.program.bind()

    def texture1_proc(self):
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

    def texture2_proc(self):
        self.texture2 = QOpenGLTexture(
            QOpenGLTexture.Target2D)
        self.texture2.create()
        self.texture2.bind(self.texUnit2)
        self.texture2.setData(self.nmap)
        self.texture2.setMinMagFilters(
            QOpenGLTexture.Nearest,
            QOpenGLTexture.Nearest)
        self.texture2.setWrapMode(
            QOpenGLTexture.DirectionS,
            QOpenGLTexture.Repeat)
        self.texture2.setWrapMode(
            QOpenGLTexture.DirectionT,
            QOpenGLTexture.Repeat)

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
        # lamp shader
        self.lampProgram = QOpenGLShaderProgram(
            self.context
        )
        #
        vshader = self.loadVertexShader("lamp")
        fshader = self.loadFragmentShader("lamp")
        print("lamp shader before init")
        self.lampShaderInit_proc(vshader, fshader)
        print("lamp shader after init")
        # end lamp shader

        # cube shader
        self.program = QOpenGLShaderProgram(self.context)
        shaderName = "light"
        vshader = self.loadVertexShader(shaderName)
        fshader = self.loadFragmentShader(shaderName)
        attrLocs = {"aPos": 0, "aNormal": 1, "aTexCoord": 2}
        print("cube shader before init")
        self.cubeShaderInit_proc(vshader, fshader, attrLocs)
        print("cube shader after init")
        # uniforms related position and light would be changed during the
        # drawing since we are handling events as well but we should set
        # those that are related material right away
        self.program.setUniformValue("material.diffuseMap", self.texUnit1)
        self.program.setUniformValue("material.specularMap", self.texUnit2)
        # end cube shader
        # end shaders

        # deal with vaos and vbos
        floatSize = ctypes.sizeof(ctypes.c_float)
        # lamp vao and vbo
        # vbo
        self.lampVbo.create()
        self.lampVbo.bind()
        self.lampVbo.allocate(self.lampVertices.tobytes(),
                              floatSize * self.lampVertices.size)
        self.lampVao.create()
        self.lampVao.bind()
        funcs.glEnableVertexAttribArray(0)  # aPos attribute
        funcs.glVertexAttribPointer(0, 3, int(pygl.GL_FLOAT),
                                    int(pygl.GL_FALSE),
                                    3 * floatSize,
                                    VoidPtr(0))
        # end lamp vao vbo

        # start cube vao vbo
        self.vbo.create()
        self.vbo.bind()
        self.vbo.allocate(self.cubeVertices.tobytes(),
                          self.cubeVertices.size * floatSize)
        # vao
        self.vao.create()
        self.vao.bind()
        funcs.glEnableVertexAttribArray(attrLocs["aPos"])  # aPos
        funcs.glVertexAttribPointer(attrLocs["aPos"], 3, int(pygl.GL_FLOAT),
                                    int(pygl.GL_FALSE),
                                    8 * floatSize, VoidPtr(0))
        funcs.glEnableVertexAttribArray(attrLocs["aNormal"])  # aNormal
        funcs.glVertexAttribPointer(attrLocs["aNormal"], 3, int(pygl.GL_FLOAT),
                                    int(pygl.GL_FALSE),
                                    8 * floatSize, VoidPtr(3 * floatSize))
        funcs.glEnableVertexAttribArray(attrLocs["aTexCoord"])
        funcs.glVertexAttribPointer(attrLocs["aTexCoord"], 2,
                                    int(pygl.GL_FLOAT),
                                    int(pygl.GL_FALSE),
                                    8 * floatSize, VoidPtr(6 * floatSize))

        # end VAOs and VBOs

        # deal with textures
        # first texture
        self.texture1_proc()
        # second texture
        self.texture2_proc()
        #
        self.lampVbo.release()
        lvaoBinder = None
        self.vbo.release()
        self.vao.release()

    def paintGL(self):
        "drawing loop"
        funcs = self.context.functions()
        # clean up what was drawn
        funcs.glClear(
            pygl.GL_COLOR_BUFFER_BIT | pygl.GL_DEPTH_BUFFER_BIT
        )
        # cubes
        # bind necessary
        self.vao.bind()
        self.vbo.bind()
        # bind the shader program
        self.program.bind()
        # set uniforms
        self.setCubeUniforms_proc()
        # end set uniforms
        # render cubes
        for i, pos in enumerate(self.cubeCoords):
            #
            self.setCubeModelUniform_proc(i, pos)
            funcs.glDrawArrays(
                pygl.GL_TRIANGLES,
                0,
                36
            )
        # unbind necessary
        self.vbo.release()
        self.program.release()
        # #### lamp
        #
        # bind necessary
        self.lampVao.bind()
        self.lampVbo.bind()
        #
        # bind shader program
        self.lampProgram.bind()
        # set uniforms
        self.setLampUniforms_proc()
        # end uniforms
        # render lamp
        funcs.glDrawArrays(
            pygl.GL_TRIANGLES,
            0,
            36
        )
