# Author: Kaan Eraslan

from PySide2 import QtWidgets
from glshader import TriangleGL
from tutorials.utils.window import GLWindow as AppWindow
import sys


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AppWindow(TriangleGL)
    window.show()
    res = app.exec_()
    sys.exit(res)
