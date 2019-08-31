# Author: Kaan Eraslan

from PySide2 import QtWidgets
from tutorials.utils.window import GLWindow as AppWindow
from gllights import LightsGL
import sys


class LightsAppWindow(AppWindow):
    "Overriding base class with event methods"

    def __init__(self,
                 glwidget: QtWidgets.QOpenGLWidget,
                 parent=None,
                 ):
        super().__init__(glwidget,
                         parent)
        #
        self.upBtn.clicked.connect(self.moveCameraForward)
        self.downBtn.clicked.connect(self.moveCameraBackward)
        self.leftBtn.clicked.connect(self.moveCameraLeft)
        self.rightBtn.clicked.connect(self.moveCameraRight)
        #
        self.camX.valueChanged.connect(self.turnCameraX)
        self.camY.valueChanged.connect(self.turnCameraY)
        #
        self.xSlider.valueChanged.connect(self.rotateCubes)
        self.ySlider.valueChanged.connect(self.rotateCubes)
        self.zSlider.valueChanged.connect(self.rotateCubes)
        #
        self.lightPosXSlider.valueChanged.connect(self.setLightPos)
        self.lightPosYSlider.valueChanged.connect(self.setLightPos)
        self.lightPosZSlider.valueChanged.connect(self.setLightPos)
        #
        self.lightRotXSlider.valueChanged.connect(self.rotateLights)
        self.lightRotYSlider.valueChanged.connect(self.rotateLights)
        self.lightRotZSlider.valueChanged.connect(self.rotateLights)
        #
        self.angleSpin.valueChanged.connect(self.setAngle)
        self.cutOff.valueChanged.connect(self.setCutOff)
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

    def setShininess(self):
        shin = self.shininessSpin.value()
        self.glWidget.changeShininess(shin)

    def setCutOff(self):
        coff = self.cutOff.value()
        self.glWidget.setCutOff(coff)

    def setAngle(self):
        angl = self.angleSpin.value()
        self.glWidget.setRotationAngle(angl)

    def setLightPos(self):
        rx = self.lightPosXSlider.value()
        ry = self.lightPosYSlider.value()
        rz = self.lightPosZSlider.value()
        self.glWidget.setLightPos(rx, ry, rz)

    def rotateLights(self):
        rx = self.lightRotXSlider.value()
        ry = self.lightRotYSlider.value()
        rz = self.lightRotZSlider.value()
        self.glWidget.rotateLight(rx, ry, rz)

    def changeDiffuseIntensity(self):
        diffr = self.diffuseIntensityRed.value()
        diffg = self.diffuseIntensityGreen.value()
        diffb = self.diffuseIntensityBlue.value()
        self.glWidget.changeLampIntensity(channel="red",
                                          val=diffr,
                                          colorType="diffuse")
        self.glWidget.changeLampIntensity(channel="green",
                                          val=diffg,
                                          colorType="diffuse")
        self.glWidget.changeLampIntensity(channel="blue",
                                          val=diffb,
                                          colorType="diffuse")

    def changeSpecularIntensity(self):
        diffr = self.specularIntensityRed.value()
        diffg = self.specularIntensityGreen.value()
        diffb = self.specularIntensityBlue.value()
        self.glWidget.changeLampIntensity(channel="red",
                                          val=diffr,
                                          colorType="specular")
        self.glWidget.changeLampIntensity(channel="green",
                                          val=diffg,
                                          colorType="specular")
        self.glWidget.changeLampIntensity(channel="blue",
                                          val=diffb,
                                          colorType="specular")

    def changeAmbientIntensity(self):
        diffr = self.ambientIntensityRed.value()
        diffg = self.ambientIntensityGreen.value()
        diffb = self.ambientIntensityBlue.value()
        self.glWidget.changeAmbientLightIntensity(diffr, diffg, diffb)

    def changeSpecularCoeffs(self):
        diffr = self.specularIntensityRedCoeff.value()
        diffg = self.specularIntensityGreenCoeff.value()
        diffb = self.specularIntensityBlueCoeff.value()
        self.glWidget.changeLampIntensityCoefficient(
            channel="red",
            val=diffr,
            colorType="specular")
        self.glWidget.changeLampIntensityCoefficient(
            channel="green",
            val=diffg,
            colorType="specular")
        self.glWidget.changeLampIntensityCoefficient(
            channel="blue",
            val=diffb,
            colorType="specular")

    def changeDiffuseCoeffs(self):
        diffr = self.diffuseIntensityRedCoeff.value()
        diffg = self.diffuseIntensityGreenCoeff.value()
        diffb = self.diffuseIntensityBlueCoeff.value()
        self.glWidget.changeLampIntensityCoefficient(
            channel="red",
            val=diffr,
            colorType="diffuse")
        self.glWidget.changeLampIntensityCoefficient(
            channel="green",
            val=diffg,
            colorType="diffuse")
        self.glWidget.changeLampIntensityCoefficient(
            channel="blue",
            val=diffb,
            colorType="diffuse")

    def changeAmbientCoeff(self):
        red = self.ambientIntensityRedCoeff.value()
        green = self.ambientIntensityGreenCoeff.value()
        blue = self.ambientIntensityBlueCoeff.value()
        self.glWidget.changeAmbientLightCoeffs(
            xval=red,
            yval=green,
            zval=blue)

    def changeAttenuation(self):
        att1 = self.attenConstant.value()
        att2 = self.attenLinear.value()
        att3 = self.attenQuadratic.value()
        self.glWidget.setLampAttenuation(attenConst=att1,
                                         attenLin=att2,
                                         attenQuad=att3,
                                         colorType="all")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = LightsAppWindow(LightsGL)
    window.show()
    res = app.exec_()
    sys.exit(res)
