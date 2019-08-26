# author: Kaan Eraslan
# license: see, LICENSE

from PySide2 import QtWidgets, QtCore, QtGui
from glshader import TriangleGL
import sys

def createSlider():
    slider = QtWidgets.QSlider(QtCore.Qt.Vertical)

    slider.setRange(0, 360 * 16)
    slider.setSingleStep(16)
    slider.setPageStep(15 * 16)
    slider.setTickInterval(15 * 16)
    slider.setTickPosition(QtWidgets.QSlider.TicksRight)
    return slider


class AppWindow(QtWidgets.QMainWindow):
    "Application window"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.glWidget = TriangleGL()
        self.xSlider = createSlider()
        self.ySlider = createSlider()
        self.zSlider = createSlider()

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(self.glWidget)
        mainLayout.addWidget(self.xSlider)
        mainLayout.addWidget(self.ySlider)
        mainLayout.addWidget(self.zSlider)
        self.mainwidget = QtWidgets.QWidget()
        self.mainwidget.setLayout(mainLayout)
        self.mainwidget.setParent(self)
        self.setWindowTitle("Triangle Opengl widget")
        self.setMinimumSize(800, 600)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AppWindow()
    window.show()
    res = app.exec_()
    sys.exit(res)
