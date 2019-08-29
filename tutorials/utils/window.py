# window for showing widgets
from PySide2 import QtWidgets, QtCore, QtGui


def createSlider():
    slider = QtWidgets.QSlider(QtCore.Qt.Vertical)

    slider.setRange(0, 360 * 16)
    slider.setSingleStep(16)
    slider.setPageStep(15 * 16)
    slider.setTickInterval(15 * 16)
    slider.setTickPosition(QtWidgets.QSlider.TicksRight)
    return slider


class GLWindow(QtWidgets.QMainWindow):
    "Application window"

    def __init__(self,
                 glwidget: QtWidgets.QOpenGLWidget,
                 parent=None,
                 ):
        super().__init__(parent)
        #
        self.glLayout = QtWidgets.QVBoxLayout()
        self.glLabel = QtWidgets.QLabel("OpenGL Widget")
        self.glWidget = glwidget()
        self.glLayout.addWidget(self.glLabel)
        self.glLayout.addWidget(self.glWidget)
        self.glLayout.setStretchFactor(self.glWidget, 1)
        self.glSection = QtWidgets.QWidget()
        self.glSection.setLayout(self.glLayout)
        #
        self.labelx = QtWidgets.QLabel("x")
        self.labely = QtWidgets.QLabel("y")
        self.labelz = QtWidgets.QLabel("z")
        self.xSlider = createSlider()
        self.ySlider = createSlider()
        self.zSlider = createSlider()
        #
        sliderLayoutV1 = QtWidgets.QVBoxLayout()
        sliderLayoutV1.addWidget(self.labelx)
        sliderLayoutV1.addWidget(self.xSlider)
        #
        sliderLayoutV2 = QtWidgets.QVBoxLayout()
        sliderLayoutV2.addWidget(self.labely)
        sliderLayoutV2.addWidget(self.ySlider)
        #
        sliderLayoutV3 = QtWidgets.QVBoxLayout()
        sliderLayoutV3.addWidget(self.labelz)
        sliderLayoutV3.addWidget(self.zSlider)
        #
        sliderSection = QtWidgets.QVBoxLayout()
        slidersLayout = QtWidgets.QHBoxLayout()
        slidersTitle = QtWidgets.QLabel('Rotate cubes')
        slidersLayout.addLayout(sliderLayoutV1)
        slidersLayout.addLayout(sliderLayoutV2)
        slidersLayout.addLayout(sliderLayoutV3)
        sliderSection.addWidget(slidersTitle)
        sliderSection.addLayout(slidersLayout)
        slidersWidget = QtWidgets.QWidget()
        slidersWidget.setLayout(sliderSection)
        # Rotate camera
        self.camX = createSlider()
        self.camY = createSlider()
        self.camlabelx = QtWidgets.QLabel("x")
        self.camlabely = QtWidgets.QLabel("y")
        self.camlabel = QtWidgets.QLabel("Rotate camera")
        camV1 = QtWidgets.QVBoxLayout()
        camV2 = QtWidgets.QVBoxLayout()
        camV1.addWidget(self.camlabelx)
        camV1.addWidget(self.camX)
        camV2.addWidget(self.camlabely)
        camV2.addWidget(self.camY)
        cams = QtWidgets.QHBoxLayout()
        cams.addLayout(camV1)
        cams.addLayout(camV2)
        camsWidget = QtWidgets.QWidget()
        camsWidget.setLayout(cams)

        camSection = QtWidgets.QVBoxLayout()
        camSection.addWidget(self.camlabel)
        camSection.addWidget(camsWidget)
        camSection.setStretchFactor(camsWidget, 1)
        camSecWidget = QtWidgets.QWidget()
        camSecWidget.setLayout(camSection)
        #
        buttonsTitel = QtWidgets.QLabel("Move camera")
        buttonsLayoutH1 = QtWidgets.QHBoxLayout()
        buttonsLayoutH2 = QtWidgets.QHBoxLayout()
        buttonsLayoutV = QtWidgets.QVBoxLayout()
        self.leftBtn = QtWidgets.QPushButton()
        self.rightBtn = QtWidgets.QPushButton()
        self.upBtn = QtWidgets.QPushButton()
        self.downBtn = QtWidgets.QPushButton()
        buttonsLayoutH1.addWidget(self.upBtn)
        buttonsLayoutH2.addWidget(self.leftBtn)
        buttonsLayoutH2.addWidget(self.downBtn)
        buttonsLayoutH2.addWidget(self.rightBtn)
        buttonsLayoutV.addWidget(buttonsTitel)
        buttonsLayoutV.addLayout(buttonsLayoutH1)
        buttonsLayoutV.addLayout(buttonsLayoutH2)
        buttonsLayoutV.addWidget(camSecWidget)
        buttonsWidget = QtWidgets.QWidget()
        buttonsWidget.setLayout(buttonsLayoutV)
        #
        self.leftBtn.setText("<")
        self.rightBtn.setText(">")
        self.upBtn.setText("^")
        self.downBtn.setText("v")

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.addWidget(self.glSection)
        mainLayout.addWidget(slidersWidget)
        mainLayout.addWidget(buttonsWidget)
        mainLayout.setStretchFactor(self.glSection, 1)
        self.mainwidget = QtWidgets.QWidget()
        self.mainwidget.setLayout(mainLayout)
        self.setCentralWidget(self.mainwidget)
        self.setWindowTitle("PySide2 OpenGL Test Window")
        self.setMinimumSize(800, 600)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
