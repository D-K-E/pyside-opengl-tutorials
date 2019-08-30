# Author: Kaan Eraslan
# purpose implements a light object


import numpy as np
import math
from PySide2.QtGui import QVector3D
from PySide2.QtGui import QColor
from utils.utils import normalize_tuple
from utils.utils import vec2vecDot


class PurePointLightSource:
    "A pure python light source implementation"

    def __init__(self,
                 posx=0.0,
                 posy=1.0,
                 posz=0.0,
                 dirx=0.0,
                 diry=-1.0,
                 dirz=-0.1,
                 cutOff=math.cos(math.radians(12.5)),
                 attenuationConstant=1.0,
                 attenuationLinear=0.7,
                 attenuationQuadratic=1.8,
                 intensityRed=255.0,
                 intensityRedCoeff=1.0,
                 intensityGreen=255.0,
                 intensityGreenCoeff=1.0,
                 intensityBlue=255.0,
                 intensityBlueCoeff=1.0):
        ""
        self.position = {"x": posx,
                         "y": posy,
                         "z": posz}
        self.direction = {"x": dirx,
                          "y": diry,
                          "z": dirz}
        self.intensity = {"r": intensityRed,
                          "g": intensityGreen,
                          "b": intensityBlue}
        self.coeffs = {"r": intensityRedCoeff,
                       "g": intensityGreenCoeff,
                       "b": intensityBlueCoeff}
        self.color = {
            "r": intensityRed * intensityRedCoeff,
            "g": intensityGreen * intensityGreenCoeff,
            "b": intensityBlue * intensityBlueCoeff
        }
        self.cutOff = cutOff
        self.attenConst = attenuationConstant
        self.attenLinear = attenuationLinear
        self.attenQuad = attenuationQuadratic
        self.attenVals = [
            # data taken on 2019-08-30 from
            # https://learnopengl.com/Lighting/Light-casters
            #distance, attenConst, attenLin, attenQaud
            [7, 1.0, 0.7, 1.8],
            [13, 1.0, 0.35, 0.44],
            [20, 1.0, 0.22, 0.20],
            [32, 1.0, 0.14, 0.07],
            [50, 1.0, 0.09, 0.032],
            [65, 1.0, 0.07, 0.017],
            [100, 1.0, 0.045, 0.0075],
            [160, 1.0, 0.027, 0.0028],
            [200, 1.0, 0.022, 0.0019],
            [325, 1.0, 0.014, 0.0007],
            [600, 1.0, 0.007, 0.0002],
            [3250, 1.0, 0.0014, 0.000007]
        ]

    def setAttenuationByTableVals(self, index: int):
        "Set attenuation values by table"
        row = self.attenVals[index]
        self.attenConst = row[1]
        self.attenLinear = row[2]
        self.attenQuad = row[3]

    def setAttenuationValuesByDistance(self,
                                       distance: float):
        ""
        self.attenVals.sort(key=lambda x: x[0])
        maxdist = self.attenVals[-1][0]
        mindist = self.attenVals[0][0]
        if distance >= maxdist:
            self.setAttenuationByTableVals(-1)
            return
        if distance <= mindist:
            self.setAttenuationByTableVals(0)
            return
        for i, dist, aconst, alin, aquad in enumerate(self.attenVals):
            if dist > distance:
                self.setAttenuationByTableVals(i)
                return

    def computeAttenuation4Distance(self, distance: float):
        "compute attenuation value for given distance"
        second = self.attenLinear * distance
        third = self.attenQuad * distance * distance
        return min(1, 1 / (self.attenConst + second + third))

    #
    def setColor(self):
        "Set color"
        self.color = {
            "r": self.intensity['r'] * self.coeffs['r'],
            "g": self.intensity['g'] * self.coeffs['g'],
            "b": self.intensity['b'] * self.coeffs['b']
        }

    def setIntensity(self, channel: str,
                     val: float):
        "Set channel intensity"
        assert val >= 0.0 and val <= 255.0
        channel = channel.lower()
        if channel == "red" or channel == "r":
            self.intensity['r'] = val
        elif channel == "green" or channel == "g":
            self.intensity['g'] = val
        elif channel == "blue" or channel == "b":
            self.intensity['b'] = val
        else:
            mess = "Unknown channel name " + channel
            mess += ", available channels are: "
            mess += "red, green, blue"
            raise ValueError(mess)
        self.setColor()

    def setCoeffs(self, channel: str,
                  val: float):
        "Set coefficients"
        assert val >= 0.0 and val <= 1.0
        channel = channel.lower()
        if channel == "red" or channel == "r":
            self.coeffs['r'] = val
        elif channel == "green" or channel == "g":
            self.coeffs['g'] = val
        elif channel == "blue" or channel == "b":
            self.coeffs['b'] = val
        else:
            mess = "Unknown channel name " + channel
            mess += ", available channels are: "
            mess += "red, green, blue"
            raise ValueError(mess)
        self.setColor()


class QtPointLightSource(PurePointLightSource):
    "A light source"

    def __init__(self,
                 position=QVector3D(0.0, 1.0, 0.0),
                 direction=QVector3D(0.0, -1.0, -0.1),
                 intensity=QVector3D(255.0,
                                     255.0,
                                     255.0),
                 coefficients=QVector3D(1.0,
                                        1.0,
                                        1.0),
                 attenuation=QVector3D(1.0, 0.7, 1.8),
                 attenuationConstant=1.0,
                 attenuationLinear=0.7,
                 attenuationQuadratic=1.8,
                 cutOff=math.cos(math.radians(12.5))
                 ):
        ""
        super().__init__(
            posx=position.x(),
            posy=position.y(),
            posz=position.z(),
            dirx=direction.x(),
            diry=direction.y(),
            dirz=direction.z(),
            cutOff=math.cos(math.radians(12.5)),
            attenuationConstant=attenuation.x(),
            attenuationLinear=attenuation.y(),
            attenuationQuadratic=attenuation.z(),
            intensityRed=intensity.x(),
            intensityRedCoeff=coefficients.x(),
            intensityGreen=intensity.y(),
            intensityGreenCoeff=coefficients.y(),
            intensityBlue=intensity.z(),
            intensityBlueCoeff=coefficients.z()
        )
        self.position = position
        self.direction = direction
        self.color = QVector3D()
        self.intensity = intensity
        self.coeffs = coefficients
        self.setColor()
        self.cutOff = cutOff
        self.attenConst = attenuationConstant
        self.attenLinear = attenuationLinear
        self.attenQuad = attenuationQuadratic
        self.attenVals = [
            # data taken on 2019-08-30 from
            # https://learnopengl.com/Lighting/Light-casters
            #distance, attenConst, attenLin, attenQaud
            [7, 1.0, 0.7, 1.8],
            [13, 1.0, 0.35, 0.44],
            [20, 1.0, 0.22, 0.20],
            [32, 1.0, 0.14, 0.07],
            [50, 1.0, 0.09, 0.032],
            [65, 1.0, 0.07, 0.017],
            [100, 1.0, 0.045, 0.0075],
            [160, 1.0, 0.027, 0.0028],
            [200, 1.0, 0.022, 0.0019],
            [325, 1.0, 0.014, 0.0007],
            [600, 1.0, 0.007, 0.0002],
            [3250, 1.0, 0.0014, 0.000007]
        ]

    def setAttenuationByTableVals(self, index: int):
        "Set attenuation values by table"
        row = self.attenVals[index]
        self.attenConst = row[1]
        self.attenLinear = row[2]
        self.attenQuad = row[3]

    def setAttenuationByDistance(self,
                                 distance: float):
        ""
        self.attenVals.sort(key=lambda x: x[0])
        maxdist = self.attenVals[-1][0]
        mindist = self.attenVals[0][0]
        if distance >= maxdist:
            self.setAttenuationByTableVals(-1)
            return
        if distance <= mindist:
            self.setAttenuationByTableVals(0)
            return
        for i, dist, aconst, alin, aquad in enumerate(self.attenVals):
            if dist > distance:
                self.setAttenuationByTableVals(i)
                return

    def setColor(self):
        "Set light source color using coeffs and intensities"
        #
        self.color = QVector3D(
            self.intensity.x() * self.coeffs.x(),
            self.intensity.y() * self.coeffs.y(),
            self.intensity.z() * self.coeffs.z()
        )

    def setIntensity(self, channel: str,
                     val: float):
        "Set channel intensity to val"
        assert val >= 0.0 and val <= 255.0
        channel = channel.lower()
        if channel == "red" or channel == "r":
            self.intensity.setX(val)
        elif channel == "green" or channel == "g":
            self.intensity.setY(val)
        elif channel == "blue" or channel == "b":
            self.intensity.setZ(val)
        else:
            mess = "Unknown channel name " + channel
            mess += ", available channels are: "
            mess += "red, green, blue"
            raise ValueError(mess)
        self.setColor()

    def setCoeffs(self, channel: str,
                  val: float):
        "Set coefficient to given intesity"
        assert val >= 0.0 and val <= 1.0
        channel = channel.lower()
        if channel == "red" or channel == "r":
            self.coeffs.setX(val)
        elif channel == "green" or channel == "g":
            self.coeffs.setY(val)
        elif channel == "blue" or channel == "b":
            self.coeffs.setZ(val)
        else:
            mess = "Unknown channel name " + channel
            mess += ", available channels are: "
            mess += "red, green, blue"
            raise ValueError(mess)
        self.setColor()


class PureLambertianReflector:
    "Object that computes lambertian reflection"

    def __init__(self, lightSource: PurePointLightSource,
                 objDiffuseReflectionCoefficientRed: float,
                 objDiffuseReflectionCoefficientGreen: float,
                 objDiffuseReflectionCoefficientBlue: float,
                 surfaceNormal: (int, int, int)):
        self.light = lightSource
        self.objR = objDiffuseReflectionCoefficientRed
        self.objG = objDiffuseReflectionCoefficientGreen
        self.objB = objDiffuseReflectionCoefficientBlue
        assert self.objR <= 1.0 and self.objR >= 0.0
        assert self.objG <= 1.0 and self.objG >= 0.0
        assert self.objB <= 1.0 and self.objB >= 0.0
        self.costheta = None
        assert len(surfaceNormal) == 3
        self.surfaceNormal = surfaceNormal
        self.setCosTheta()
        self.reflection = {}
        self.setLambertianReflection()

    def setCosTheta(self):
        ""
        lightDir = self.light.direction
        lightDir = (lightDir['x'], lightDir['y'], lightDir["z"])
        normLight = normalize_tuple(lightDir)
        normSurf = normalize_tuple(self.surfaceNormal)
        self.costheta = vec2vecDot(normSurf, normLight)

    def setLambertianReflection(self):
        "compute reflection"
        red = self.light.intensity['r'] * self.objR * self.costheta
        green = self.light.intensity['g'] * self.objG * self.costheta
        blue = self.light.intensity['b'] * self.objB * self.costheta
        self.reflection['r'] = red
        self.reflection['g'] = green
        self.reflection['b'] = blue


class PureLambertianReflectorAmbient(PureLambertianReflector):
    "Pure python implementation of lambertian reflector with ambient light"

    def __init__(self,
                 lightSource: PurePointLightSource,
                 ambientLight: PurePointLightSource,
                 objDiffuseReflectionCoefficientRed: float,
                 objDiffuseReflectionCoefficientGreen: float,
                 objDiffuseReflectionCoefficientBlue: float,
                 surfaceNormal: (int, int, int)):
        super().__init__(
            lightSource,
            objDiffuseReflectionCoefficientRed,
            objDiffuseReflectionCoefficientGreen,
            objDiffuseReflectionCoefficientBlue,
            surfaceNormal
        )
        self.setCosTheta()
        self.setLambertianReflection()
        self.ambientLight = ambientLight

    def setLambertianReflectionWithAmbient(self):
        red = self.reflection['r'] + self.ambientLight.color['r']
        green = self.reflection['g'] + self.ambientLight.color['g']
        blue = self.reflection['b'] + self.ambientLight.color['b']
        self.reflection = {"r": red, "g": green, "b": blue}


class PureLight:
    def __init__(self,
                 posx=0.0,
                 posy=1.0,
                 posz=0.0,
                 dirx=0.0,
                 diry=-1.0,
                 dirz=-0.1,
                 ambientRed=1.0,
                 ambientBlue=1.0,
                 ambientGreen=1.0,
                 diffuseRed=1.0,
                 diffuseBlue=1.0,
                 diffuseGreen=1.0,
                 specularRed=1.0,
                 specularGreen=1.0,
                 specularBlue=1.0,
                 ):
        ""
        self.position = {"x": posx,
                         "y": posy,
                         "z": posz}
        self.direction = {"x": dirx,
                          "y": diry,
                          "z": dirz}
        self.ambient = {"r": ambientRed,
                        "g": ambientGreen,
                        "b": ambientBlue}
        self.diffuse = {"r": diffuseRed,
                        "g": diffuseGreen,
                        "b": diffuseBlue}
        self.specular = {"r": specularRed,
                         "g": specularGreen,
                         "b": specularBlue}

    def getSpecular(self):
        return (self.specular["r"],
                self.specular["g"],
                self.specular["b"])

    def getPosition(self):
        return (self.position["x"],
                self.position["y"],
                self.position["z"])

    def getDirection(self):
        return (self.direction["x"],
                self.direction["y"],
                self.direction["z"])

    def getAmbient(self):
        return (self.ambient["r"],
                self.ambient["g"],
                self.ambient["b"])

    def getDiffuse(self):
        return (self.diffuse["r"],
                self.diffuse["g"],
                self.diffuse["b"])

    def getCutOff(self):
        return self.cutOff


class QtLight:
    "Light"

    def __init__(self,
                 position=QVector3D(0.0, 1.0, 0.0),
                 direction=QVector3D(0.0, -1.0, -0.1),
                 ambient=QColor(1.0, 1.0, 1.0),
                 diffuse=QColor(1.0, 1.0, 1.0),
                 specular=QColor(1.0, 1.0, 1.0),
                 cutOff=math.cos(math.radians(12.5)),
                 attenuationConstant=1.0,
                 attenuationLinear=0.7,
                 attenuationQuadratic=1.8
                 ):
        ""
        self.position = position
        self.direction = direction
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.cutOff = cutOff
        self.attenVals = [
            #distance, attenConst, attenLin, attenQaud
            [7, 1.0, 0.7, 1.8],
            [13, 1.0, 0.35, 0.44],
            [20, 1.0, 0.22, 0.20],
            [32, 1.0, 0.14, 0.07],
            [50, 1.0, 0.09, 0.032],
            [65, 1.0, 0.07, 0.017],
            [100, 1.0, 0.045, 0.0075],
            [160, 1.0, 0.027, 0.0028],
            [200, 1.0, 0.022, 0.0019],
            [325, 1.0, 0.014, 0.0007],
            [600, 1.0, 0.007, 0.0002],
            [3250, 1.0, 0.0014, 0.000007]
        ]

    def toPureLight(self):
        "Transform to pure python"
        return PureLight(
            posx=self.position.x(),
            posy=self.position.y(),
            posz=self.position.z(),
            dirx=self.position.x(),
            diry=self.position.y(),
            dirz=self.position.z(),
            ambientRed=self.ambient.red(),
            ambientBlue=self.ambient.blue(),
            ambientGreen=self.ambient.green(),
            diffuseRed=self.diffuse.red(),
            diffuseBlue=self.diffuse.blue(),
            diffuseGreen=self.diffuse.green(),
            specularRed=self.specular.red(),
            specularGreen=self.specular.green(),
            specularBlue=self.specular.blue(),
            cutOff=self.cutOff
        )

    def fromPureLight(self, light: PureLight):
        ""
        self.position = QVector3D(
            light.position["x"],
            light.position["y"],
            light.position["z"]
        )
        self.direction = QVector3D(
            light.direction["x"],
            light.direction["y"],
            light.direction["z"]
        )
        self.ambient = QColor(
            light.ambient["r"],
            light.ambient["g"],
            light.ambient["b"]
        )
        self.diffuse = QColor(
            light.diffuse["r"],
            light.diffuse["g"],
            light.diffuse["b"]
        )
        self.specular = QColor(
            light.specular["r"],
            light.specular["g"],
            light.specular["b"]
        )
        self.cutOff = light.cutOff
