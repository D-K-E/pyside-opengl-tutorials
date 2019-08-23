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
        projectdir = os.getcwd()
        self.shaders = {
            "portableTriangle": {
                "fragment": """
uniform mediump vec4 color;

void main(void)
{
    gl_FragColor = color;
}""",
                "vertex": """
attribute highp vec3 aPos;
void main(void)
{
    gl_Position = vec4(aPos, 1.0);
}

""",

            }
        }
        self.core = "--coreprofile" in QCoreApplication.arguments()

        # opengl data related
        self.context = QOpenGLContext()
        self.vao = QOpenGLVertexArrayObject()
        self.vbo = QOpenGLBuffer(QOpenGLBuffer.VertexBuffer)
        self.program = QOpenGLShaderProgram()

        # some vertex data for corners of triangle
        self.vertexData = np.array(
            [-0.5, -0.5, 0.0,  # x, y, z
             0.5, -0.5, 0.0,  # x, y, z
             0.0, 0.5, 0.0],  # x, y, z
            dtype=ctypes.c_float
        )
        # triangle color
        self.triangleColor = QVector4D(0.5, 0.5, 0.0, 0.0)  # yellow triangle
        # notice the correspondance the vec4 of fragment shader 
        # and our choice here

    def loadShader(self,
                   shaderName: str,
                   shaderType: str):
        "Load shader"
        shader = self.shaders[shaderName]
        shaderSource = shader[shaderType]
        if shaderType == "vertex":
            shader = QOpenGLShader(QOpenGLShader.Vertex)
        else:
            shader = QOpenGLShader(QOpenGLShader.Fragment)
        #
        isCompiled = shader.compileSourceCode(shaderSource)

        if isCompiled is False:
            print(shader.log())
            raise ValueError(
                "{0} shader {2} known as {1} is not compiled".format(
                    shaderType, shaderName, shaderSource
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
        self.program.bindAttributeLocation("aPos", 0)

        # link shader program
        isLinked = self.program.link()
        print("shader program is linked: ", isLinked)

        # bind the program
        self.program.bind()

        # specify uniform value
        colorLoc = self.program.uniformLocation("color")
        self.program.setUniformValue(colorLoc,
                                     self.triangleColor)

        # self.useShader("triangle")

        # deal with vao and vbo

        # create vao and vbo

        # vao
        isVao = self.vao.create()
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)

        # vbo
        isVbo = self.vbo.create()
        isBound = self.vbo.bind()

        # check if vao and vbo are created
        print('vao created: ', isVao)
        print('vbo created: ', isVbo)

        floatSize = ctypes.sizeof(ctypes.c_float)

        # allocate space on buffer
        self.vbo.allocate(self.vertexData.tobytes(),
                          floatSize * self.vertexData.size)
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
        vaoBinder = QOpenGLVertexArrayObject.Binder(self.vao)
        self.program.bind()
        funcs.glDrawArrays(pygl.GL_TRIANGLES,
                           0,
                           3)
        self.program.release()
        vaoBinder = None
