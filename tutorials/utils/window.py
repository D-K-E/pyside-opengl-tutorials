# window for showing widgets
from PySide2 import QtWidgets, QtCore
from PySide2.QtWidgets import QLabel
from PySide2.QtWidgets import QVBoxLayout
from PySide2.QtWidgets import QHBoxLayout
from PySide2.QtWidgets import QWidget


def createSlider():
    slider = QtWidgets.QSlider(QtCore.Qt.Vertical)

    slider.setRange(0, 360 * 16)
    slider.setSingleStep(16)
    slider.setPageStep(15 * 16)
    slider.setTickInterval(15 * 16)
    slider.setTickPosition(QtWidgets.QSlider.TicksRight)
    return slider


def createDSpinBox(smin: float, smax: float,
                   step: float, setval=1.0):
    spinbox = QtWidgets.QDoubleSpinBox()
    spinbox.setRange(smin, smax)
    spinbox.setSingleStep(step)
    spinbox.setValue(setval)
    return spinbox


class GLWindow(QtWidgets.QMainWindow):
    "Application window"

    def __init__(self,
                 glwidget: QtWidgets.QOpenGLWidget,
                 parent=None,
                 ):
        super().__init__(parent)
        # OpenGL Widget
        self.glLayout = QVBoxLayout()
        self.glLabel = QLabel("OpenGL Widget")
        self.glWidget = glwidget()
        self.glLayout.addWidget(self.glLabel)
        self.glLayout.addWidget(self.glWidget)
        self.glLayout.setStretchFactor(self.glWidget, 1)
        self.glSection = QWidget()
        self.glSection.setLayout(self.glLayout)
        # Cube Controls
        self.labelx = QLabel("x")
        self.labely = QLabel("y")
        self.labelz = QLabel("z")
        self.xSlider = createSlider()
        self.ySlider = createSlider()
        self.zSlider = createSlider()
        #
        sliderLayoutV1 = QVBoxLayout()
        sliderLayoutV1.addWidget(self.labelx)
        sliderLayoutV1.addWidget(self.xSlider)
        #
        sliderLayoutV2 = QVBoxLayout()
        sliderLayoutV2.addWidget(self.labely)
        sliderLayoutV2.addWidget(self.ySlider)
        #
        sliderLayoutV3 = QVBoxLayout()
        sliderLayoutV3.addWidget(self.labelz)
        sliderLayoutV3.addWidget(self.zSlider)
        #
        sliderSection = QVBoxLayout()
        slidersLayout = QHBoxLayout()
        slidersTitle = QLabel('Rotate cubes')
        slidersLayout.addLayout(sliderLayoutV1)
        slidersLayout.addLayout(sliderLayoutV2)
        slidersLayout.addLayout(sliderLayoutV3)
        sliderSection.addWidget(slidersTitle)
        sliderSection.addLayout(slidersLayout)
        slidersWidget = QWidget()
        slidersWidget.setLayout(sliderSection)
        # Camera Controls
        # Rotate camera
        self.camX = createSlider()
        self.camY = createSlider()
        self.camlabelx = QLabel("x")
        self.camlabely = QLabel("y")
        self.camlabel = QLabel("Rotate camera")
        camV1 = QVBoxLayout()
        camV2 = QVBoxLayout()
        camV1.addWidget(self.camlabelx)
        camV1.addWidget(self.camX)
        camV2.addWidget(self.camlabely)
        camV2.addWidget(self.camY)
        cams = QHBoxLayout()
        cams.addLayout(camV1)
        cams.addLayout(camV2)
        camsWidget = QWidget()
        camsWidget.setLayout(cams)
        # cube and cam sliders

        camSection = QVBoxLayout()
        camSection.addWidget(self.camlabel)
        camSection.addWidget(camsWidget)
        camSection.setStretchFactor(camsWidget, 1)
        camSecWidget = QWidget()
        camSecWidget.setLayout(camSection)
        #
        camsCubes = QHBoxLayout()
        camsCubes.addWidget(slidersWidget)
        camsCubes.addWidget(camSecWidget)
        #
        buttonsTitel = QLabel("Move camera")
        buttonsLayoutH1 = QHBoxLayout()
        buttonsLayoutH2 = QHBoxLayout()
        buttonsLayoutV = QVBoxLayout()
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
        buttonsLayoutV.addLayout(camsCubes)
        buttonsWidget = QWidget()
        buttonsWidget.setLayout(buttonsLayoutV)
        #
        self.leftBtn.setText("<")
        self.rightBtn.setText(">")
        self.upBtn.setText("^")
        self.downBtn.setText("v")
        self.leftBtn.setAutoRepeat(True)
        self.leftBtn.setAutoRepeatInterval(15)  # repeat at x milisecond
        self.leftBtn.setAutoRepeatDelay(100)  # start repeating after
        # x milisecond
        self.rightBtn.setAutoRepeat(True)
        self.rightBtn.setAutoRepeatDelay(100)
        self.rightBtn.setAutoRepeatInterval(15)
        #
        self.downBtn.setAutoRepeat(True)
        self.downBtn.setAutoRepeatDelay(100)
        self.downBtn.setAutoRepeatInterval(15)
        #
        self.upBtn.setAutoRepeat(True)
        self.upBtn.setAutoRepeatDelay(100)
        self.upBtn.setAutoRepeatInterval(15)
        #
        # Light controls
        #
        lightSection = QWidget()
        lightSectionLayout = QVBoxLayout()
        lightSectionLabel = QLabel("Light Controls")
        lightSectionWidgetsLayout = QVBoxLayout()
        #
        slidersLayout = QHBoxLayout()
        # light position
        self.lightPosWidget = QWidget()
        self.lightPosTitle = QLabel("light position")
        self.lightPosLayout = QVBoxLayout()
        lightPosWidgetsLayout = QHBoxLayout()
        #
        self.lightPosXSlider = createSlider()
        self.lightPosXTitle = QLabel("x")
        posxLayout = QVBoxLayout()
        posxLayout.addWidget(self.lightPosXTitle)
        posxLayout.addWidget(self.lightPosXSlider)
        #
        self.lightPosYSlider = createSlider()
        self.lightPosYTitle = QLabel("y")
        posyLayout = QVBoxLayout()
        posyLayout.addWidget(self.lightPosYTitle)
        posyLayout.addWidget(self.lightPosYSlider)
        #
        self.lightPosZSlider = createSlider()
        self.lightPosZTitle = QLabel("z")
        poszLayout = QVBoxLayout()
        poszLayout.addWidget(self.lightPosZTitle)
        poszLayout.addWidget(self.lightPosZSlider)
        #
        lightPosWidgetsLayout.addLayout(posxLayout)
        lightPosWidgetsLayout.addLayout(posyLayout)
        lightPosWidgetsLayout.addLayout(poszLayout)
        self.lightPosLayout.addWidget(self.lightPosTitle)
        self.lightPosLayout.addLayout(lightPosWidgetsLayout)
        self.lightPosWidget.setLayout(self.lightPosLayout)
        slidersLayout.addWidget(self.lightPosWidget)
        # end light position
        # light rotation
        self.lightRotWidget = QWidget()
        self.lightRotTitle = QLabel("light rotation")
        self.lightRotLayout = QVBoxLayout()
        lightRotWidgetsLayout = QHBoxLayout()
        #
        self.lightRotXSlider = createSlider()
        self.lightRotXTitle = QLabel("x")
        RotxLayout = QVBoxLayout()
        RotxLayout.addWidget(self.lightRotXTitle)
        RotxLayout.addWidget(self.lightRotXSlider)
        #
        self.lightRotYSlider = createSlider()
        self.lightRotYTitle = QLabel("y")
        RotyLayout = QVBoxLayout()
        RotyLayout.addWidget(self.lightRotYTitle)
        RotyLayout.addWidget(self.lightRotYSlider)
        #
        self.lightRotZSlider = createSlider()
        self.lightRotZTitle = QLabel("z")
        RotzLayout = QVBoxLayout()
        RotzLayout.addWidget(self.lightRotZTitle)
        RotzLayout.addWidget(self.lightRotZSlider)
        #
        lightRotWidgetsLayout.addLayout(RotxLayout)
        lightRotWidgetsLayout.addLayout(RotyLayout)
        lightRotWidgetsLayout.addLayout(RotzLayout)
        #
        self.lightRotLayout.addWidget(self.lightRotTitle)
        self.lightRotLayout.addLayout(lightRotWidgetsLayout)
        self.lightRotWidget.setLayout(self.lightRotLayout)
        slidersLayout.addWidget(self.lightRotWidget)
        # end light rotation
        #
        spinsLayout = QVBoxLayout()
        #
        lightTypesLayout = QVBoxLayout()
        adsLayout = QHBoxLayout()
        # ambient light
        ambientWidget = QWidget()
        ambientLayout = QVBoxLayout()
        ambientTitle = QLabel("ambient")
        ambientWidgetsLayout = QVBoxLayout()
        # ambient red
        self.ambientIntensityRed = createDSpinBox(0.0, 255.0, 0.5, 255.0)
        self.ambientIntensityRedCoeff = createDSpinBox(0.0, 1.0, 0.05)
        intenCoeff = QHBoxLayout()
        intenCoeff.addWidget(self.ambientIntensityRed)
        intenCoeff.addWidget(self.ambientIntensityRedCoeff)
        self.ambientRedLabel = QLabel("Red")
        channelLayout = QVBoxLayout()
        channelLayout.addWidget(self.ambientRedLabel)
        channelLayout.addLayout(intenCoeff)
        ambientWidgetsLayout.addLayout(channelLayout)
        # end ambient red
        # ambient green
        self.ambientIntensityGreen = createDSpinBox(0.0, 255.0, 0.5, 255.0)
        self.ambientIntensityGreenCoeff = createDSpinBox(0.0, 1.0, 0.05)
        intenCoeff = QHBoxLayout()
        intenCoeff.addWidget(self.ambientIntensityGreen)
        intenCoeff.addWidget(self.ambientIntensityGreenCoeff)
        self.ambientGreenLabel = QLabel("Green")
        channelLayout = QVBoxLayout()
        channelLayout.addWidget(self.ambientGreenLabel)
        channelLayout.addLayout(intenCoeff)
        ambientWidgetsLayout.addLayout(channelLayout)
        # end ambient green
        # ambient blue
        self.ambientIntensityBlue = createDSpinBox(0.0, 255.0, 0.5, 255.0)
        self.ambientIntensityBlueCoeff = createDSpinBox(0.0, 1.0, 0.05)
        intenCoeff = QHBoxLayout()
        intenCoeff.addWidget(self.ambientIntensityBlue)
        intenCoeff.addWidget(self.ambientIntensityBlueCoeff)
        self.ambientBlueLabel = QLabel("Blue")
        channelLayout = QVBoxLayout()
        channelLayout.addWidget(self.ambientBlueLabel)
        channelLayout.addLayout(intenCoeff)
        # end ambient blue
        ambientWidgetsLayout.addLayout(channelLayout)
        ambientLayout.addWidget(ambientTitle)
        ambientLayout.addLayout(ambientWidgetsLayout)
        ambientWidget.setLayout(ambientLayout)
        #
        adsLayout.addWidget(ambientWidget)
        # end ambient light
        # diffuse light
        diffuseWidget = QWidget()
        diffuseLayout = QVBoxLayout()
        diffuseTitle = QLabel("diffuse")
        diffuseWidgetsLayout = QVBoxLayout()
        # diffuse red
        self.diffuseIntensityRed = createDSpinBox(0.0, 255.0, 0.5, 255.0)
        self.diffuseIntensityRedCoeff = createDSpinBox(0.0, 1.0, 0.05)
        intenCoeff = QHBoxLayout()
        intenCoeff.addWidget(self.diffuseIntensityRed)
        intenCoeff.addWidget(self.diffuseIntensityRedCoeff)
        self.diffuseRedLabel = QLabel("Red")
        channelLayout = QVBoxLayout()
        channelLayout.addWidget(self.diffuseRedLabel)
        channelLayout.addLayout(intenCoeff)
        diffuseWidgetsLayout.addLayout(channelLayout)
        # end diffuse red
        # diffuse green
        self.diffuseIntensityGreen = createDSpinBox(0.0, 255.0, 0.5, 255.0)
        self.diffuseIntensityGreenCoeff = createDSpinBox(0.0, 1.0, 0.05)
        intenCoeff = QHBoxLayout()
        intenCoeff.addWidget(self.diffuseIntensityGreen)
        intenCoeff.addWidget(self.diffuseIntensityGreenCoeff)
        self.diffuseGreenLabel = QLabel("Green")
        channelLayout = QVBoxLayout()
        channelLayout.addWidget(self.diffuseGreenLabel)
        channelLayout.addLayout(intenCoeff)
        diffuseWidgetsLayout.addLayout(channelLayout)
        # end diffuse green
        # diffuse blue
        self.diffuseIntensityBlue = createDSpinBox(0.0, 255.0, 0.5, 255.0)
        self.diffuseIntensityBlueCoeff = createDSpinBox(0.0, 1.0, 0.05)
        intenCoeff = QHBoxLayout()
        intenCoeff.addWidget(self.diffuseIntensityBlue)
        intenCoeff.addWidget(self.diffuseIntensityBlueCoeff)
        self.diffuseBlueLabel = QLabel("Blue")
        channelLayout = QVBoxLayout()
        channelLayout.addWidget(self.diffuseBlueLabel)
        channelLayout.addLayout(intenCoeff)
        # end diffuse blue
        diffuseWidgetsLayout.addLayout(channelLayout)
        diffuseLayout.addWidget(diffuseTitle)
        diffuseLayout.addLayout(diffuseWidgetsLayout)
        diffuseWidget.setLayout(diffuseLayout)
        #
        adsLayout.addWidget(diffuseWidget)
        # end diffuse light
        # specular light
        specularWidget = QWidget()
        specularLayout = QVBoxLayout()
        specularTitle = QLabel("specular")
        specularWidgetsLayout = QVBoxLayout()
        # specular red
        self.specularIntensityRed = createDSpinBox(0.0, 255.0, 0.5, 255.0)
        self.specularIntensityRedCoeff = createDSpinBox(0.0, 1.0, 0.05)
        intenCoeff = QHBoxLayout()
        intenCoeff.addWidget(self.specularIntensityRed)
        intenCoeff.addWidget(self.specularIntensityRedCoeff)
        self.specularRedLabel = QLabel("Red")
        channelLayout = QVBoxLayout()
        channelLayout.addWidget(self.specularRedLabel)
        channelLayout.addLayout(intenCoeff)
        specularWidgetsLayout.addLayout(channelLayout)
        # end specular red
        # specular green
        self.specularIntensityGreen = createDSpinBox(0.0, 255.0, 0.5, 255.0)
        self.specularIntensityGreenCoeff = createDSpinBox(0.0, 1.0, 0.05)
        intenCoeff = QHBoxLayout()
        intenCoeff.addWidget(self.specularIntensityGreen)
        intenCoeff.addWidget(self.specularIntensityGreenCoeff)
        self.specularGreenLabel = QLabel("Green")
        channelLayout = QVBoxLayout()
        channelLayout.addWidget(self.specularGreenLabel)
        channelLayout.addLayout(intenCoeff)
        specularWidgetsLayout.addLayout(channelLayout)
        # end specular green
        # specular blue
        self.specularIntensityBlue = createDSpinBox(0.0, 255.0, 0.5, 255.0)
        self.specularIntensityBlueCoeff = createDSpinBox(0.0, 1.0, 0.05)
        intenCoeff = QHBoxLayout()
        intenCoeff.addWidget(self.specularIntensityBlue)
        intenCoeff.addWidget(self.specularIntensityBlueCoeff)
        self.specularBlueLabel = QLabel("Blue")
        channelLayout = QVBoxLayout()
        channelLayout.addWidget(self.specularBlueLabel)
        channelLayout.addLayout(intenCoeff)
        # end specular blue
        specularWidgetsLayout.addLayout(channelLayout)
        specularLayout.addWidget(specularTitle)
        specularLayout.addLayout(specularWidgetsLayout)
        specularWidget.setLayout(specularLayout)
        #
        adsLayout.addWidget(specularWidget)
        spinsLayout.addLayout(adsLayout)
        # end specular light
        # attenuation
        attenuationWidget = QWidget()
        attenuationLayout = QVBoxLayout()
        attenuationTitle = QLabel("attenuation")
        attenuationWidgetsLayout = QHBoxLayout()
        # constant attenuation
        self.attenConstant = createDSpinBox(0.1, 1.0, 0.1)
        self.attenConstant.setValue(1.0)
        self.attenConstLabel = QLabel("constant")
        attenConstV = QVBoxLayout()
        attenConstV.addWidget(self.attenConstLabel)
        attenConstV.addWidget(self.attenConstant)
        attenuationWidgetsLayout.addLayout(attenConstV)
        # linear attenuation
        self.attenLinear = createDSpinBox(0.001, 10.0, 0.1, 0.7)
        self.attenLinearLabel = QLabel("linear")
        attenLinearV = QVBoxLayout()
        attenLinearV.addWidget(self.attenLinearLabel)
        attenLinearV.addWidget(self.attenLinear)
        attenuationWidgetsLayout.addLayout(attenLinearV)
        # quadratic attenuation
        self.attenQuadratic = createDSpinBox(0.001, 10.0, 1.8)
        self.attenQuadraticLabel = QLabel("quadratic")
        attenQuadraticV = QVBoxLayout()
        attenQuadraticV.addWidget(self.attenQuadraticLabel)
        attenQuadraticV.addWidget(self.attenQuadratic)
        attenuationWidgetsLayout.addLayout(attenQuadraticV)
        #
        attenuationLayout.addWidget(attenuationTitle)
        attenuationLayout.addLayout(attenuationWidgetsLayout)
        attenuationWidget.setLayout(attenuationLayout)
        #
        spinsLayout.addWidget(attenuationWidget)
        # end attenuation
        # angle and shininess
        otherWidget = QWidget()
        otherLayout = QHBoxLayout()
        # angle
        angLayout = QVBoxLayout()
        anglbl = QLabel("angle")
        self.angleSpin = createDSpinBox(1.0, 90.0, 1.0, 30.0)
        angLayout.addWidget(anglbl)
        angLayout.addWidget(self.angleSpin)
        #
        otherLayout.addLayout(angLayout)
        # end angle
        # shininess
        shinLayout = QVBoxLayout()
        shinlbl = QLabel("shininess")
        self.shininessSpin = createDSpinBox(0.01, 250.0, 0.01, 20.0)
        shinLayout.addWidget(shinlbl)
        shinLayout.addWidget(self.shininessSpin)
        #
        otherLayout.addLayout(shinLayout)
        # end shininess
        # cut off
        cutOffTitle = QLabel("Cut Off")
        cutOffLayout = QVBoxLayout()
        self.cutOff = createDSpinBox(0.1, 45.0, 0.1)
        cutOffLayout.addWidget(cutOffTitle)
        cutOffLayout.addWidget(self.cutOff)
        #
        otherLayout.addLayout(cutOffLayout)
        # end cut off
        otherWidget.setLayout(otherLayout)
        spinsLayout.addWidget(otherWidget)
        # end other widgets
        lightSectionWidgetsLayout.addLayout(spinsLayout)
        lightSectionWidgetsLayout.addLayout(slidersLayout)
        #
        lightSectionLayout.addWidget(lightSectionLabel)
        lightSectionLayout.addLayout(lightSectionWidgetsLayout)
        lightSection.setLayout(lightSectionLayout)
        # end light controls
        #
        mainLayout = QHBoxLayout()
        mainLayout.addWidget(self.glSection)
        mainLayout.addWidget(buttonsWidget)
        mainLayout.addWidget(lightSection)
        mainLayout.setStretchFactor(self.glSection, 1)
        self.mainwidget = QWidget()
        self.mainwidget.setLayout(mainLayout)
        self.setCentralWidget(self.mainwidget)
        self.setWindowTitle("PySide2 OpenGL Test Window")
        self.setMinimumSize(800, 600)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
