# Author: Kaan Eraslan

from PySide2 import QtWidgets
from tutorials.utils.window import GLWindow as AppWindow
from glevents import EventsGL
import sys


class EventAppWindow(AppWindow):
    "Overriding base class with event methods"

    def __init__(self,
                 glwidget: QtWidgets.QOpenGLWidget,
                 parent=None,
                 ):
        super().__init__(glwidget,
                         parent)
        self.camX.setRange(-520.0, 520.0)
        self.camY.setRange(-520.0, 520.0)
        self.xSlider.setRange(-180.0, 180.0)
        self.ySlider.setRange(-180.0, 180.0)
        self.zSlider.setRange(-180.0, 180.0)
        self.upBtn.clicked.connect(self.moveCameraForward)
        self.downBtn.clicked.connect(self.moveCameraBackward)
        self.leftBtn.clicked.connect(self.moveCameraLeft)
        self.rightBtn.clicked.connect(self.moveCameraRight)
        self.camX.valueChanged.connect(self.turnCameraX)
        self.camY.valueChanged.connect(self.turnCameraY)
        self.xSlider.valueChanged.connect(self.rotateCubes)
        self.ySlider.valueChanged.connect(self.rotateCubes)
        self.zSlider.valueChanged.connect(self.rotateCubes)
        #
        self.lastCamXVal = self.camX.value()
        #
        self.lastCamYVal = self.camY.value()

    def moveGLCamera(self, direction: str):
        self.glWidget.moveCamera(direction)

    def moveCameraForward(self):
        self.moveGLCamera("forward")

    def moveCameraBackward(self):
        self.moveGLCamera("backward")

    def moveCameraLeft(self):
        self.moveGLCamera("left")

    def moveCameraRight(self):
        self.moveGLCamera("right")

    def turnCameraX(self, newVal: int):
        "Turn camera around"
        offsetx = newVal - self.lastCamXVal
        valy = self.camY.value() - self.lastCamYVal
        self.glWidget.turnAround(x=float(offsetx),
                                 y=float(valy))
        self.lastCamXVal = newVal

    def turnCameraY(self, newVal: int):
        "Turn camera around"
        offsety = newVal - self.lastCamYVal
        valx = self.camX.value() - self.lastCamXVal
        self.glWidget.turnAround(x=float(valx),
                                 y=float(offsety))
        self.lastCamYVal = newVal

    def rotateCubes(self):
        rx = self.xSlider.value()
        ry = self.ySlider.value()
        rz = self.zSlider.value()
        self.glWidget.rotateCubes(rx, ry, rz)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = EventAppWindow(EventsGL)
    window.show()
    res = app.exec_()
    sys.exit(res)
