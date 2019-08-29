# Author: Kaan Eraslan

from PySide2 import QtWidgets
from tutorials.utils.window import GLWindow as AppWindow
from gltexture import TextureGL
import sys


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = AppWindow(TextureGL)
    window.show()
    res = app.exec_()
    sys.exit(res)
