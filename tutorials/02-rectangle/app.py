# Author: Kaan Eraslan

from PySide2 import QtWidgets, QtCore, QtGui
from glrectangle import RectangleGL
from tutorials.utils.window import GLWindow as AppWindow
import sys


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AppWindow(RectangleGL)
    window.show()
    res = app.exec_()
    sys.exit(res)
