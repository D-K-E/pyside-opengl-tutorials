# Author: Kaan Eraslan
# purpose implements a light object


import math
from PySide2.QtGui import QVector3D
from tutorials.utils.utils import normalize_tuple
from tutorials.utils.utils import vec2vecDot
from tutorials.utils.utils import crossProduct


class PureLightSource:
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
                 intensityRed=1.0,
                 intensityRedCoeff=1.0,
                 intensityGreen=1.0,
                 intensityGreenCoeff=1.0,
                 intensityBlue=1.0,
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
            # distance, attenConst, attenLin, attenQaud
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

    def computeAttenuation4Distance(self,
                                    distance: float):
        "compute attenuation value for given distance"
        second = self.attenLinear * distance
        third = self.attenQuad * distance * distance
        return min(1, 1 / (self.attenConst + second + third))

    def setAttenuation(self, **kwargs):
        "set attenuation"
        self.attenConst = kwargs['aConst']
        self.attenLinear = kwargs['aLin']
        self.attenQuad = kwargs['aQuad']

    def setColor(self):
        "Set color"
        self.color = {
            "r": self.intensity['r'] * self.coeffs['r'],
            "g": self.intensity['g'] * self.coeffs['g'],
            "b": self.intensity['b'] * self.coeffs['b']
        }

    def setIntensity(self, **kwargs):
        "Set channel intensity"
        name = kwargs['channel']
        val = kwargs['val']
        assert val >= 0.0 and val <= 255.0
        name = name.lower()
        if name == "red" or name == "r":
            self.intensity['r'] = val
        elif name == "green" or name == "g":
            self.intensity['g'] = val
        elif name == "blue" or name == "b":
            self.intensity['b'] = val
        else:
            mess = "Unknown name name " + name
            mess += ", available channels are: "
            mess += "red, green, blue"
            raise ValueError(mess)
        self.setColor()

    def setCoeffs(self, **kwargs):
        "Set coefficients"
        name = kwargs['channel']
        val = kwargs['val']
        assert val >= 0.0 and val <= 1.0
        name = name.lower()
        if name == "red" or name == "r":
            self.coeffs['r'] = val
        elif name == "green" or name == "g":
            self.coeffs['g'] = val
        elif name == "blue" or name == "b":
            self.coeffs['b'] = val
        else:
            mess = "Unknown channel name " + name
            mess += ", available channels are: "
            mess += "red, green, blue"
            raise ValueError(mess)
        self.setColor()

    def setPosition(self, **kwargs):
        "set position of the light source"
        x, y, z = kwargs['x'], kwargs['y'], kwargs['z']
        self.position = {"x": x, "y": y, "z": z}

    def setDirection(self, **kwargs):
        "set direction of the light source"
        x, y, z = kwargs['x'], kwargs['y'], kwargs['z']
        self.direction = {"x": x, "y": y, "z": z}

    def setCutOff(self, val: float):
        ""
        self.cutOff = math.cos(math.radians(val))

    def getCoeffAverage(self):
        "Get the average value of its coefficients"
        red, green = self.coeffs['r'], self.coeffs['g']
        blue = self.coeffs['b']
        return (red + green + blue) / 3

    def __str__(self):
        ""
        mess = "Light Source:\n position {0},\n direction {1},\n intensity {2}"
        mess += ",\n coefficients {3},\n color {4},\n cutOff value {5}"
        mess += ",\n attenuation constant {6},\n attenuation linear {7}"
        mess += ",\n attenuation quadratic {8}"
        return mess.format(str(self.position), str(self.direction),
                           str(self.intensity), str(self.coeffs),
                           str(self.color), str(self.cutOff),
                           str(self.attenConst), str(self.attenLinear),
                           str(self.attenQuad))


class QtLightSource(PureLightSource):
    "A light source"

    def __init__(self,
                 position=QVector3D(0.0, 1.0, 0.0),
                 direction=QVector3D(0.0, -1.0, -0.1),
                 intensity=QVector3D(1.0,
                                     1.0,
                                     1.0),
                 coefficients=QVector3D(1.0,
                                        1.0,
                                        1.0),
                 attenuation=QVector3D(1.0, 0.7, 1.8),
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
        self.attenuation = attenuation

    def setAttenuationByTableVals(self, index: int):
        "Set attenuation values by table"
        row = self.attenVals[index]
        self.attenConst = row[1]
        self.attenLinear = row[2]
        self.attenQuad = row[3]
        self.attenuation = QVector3D(row[1], row[2], row[3])

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

    def setAttenuation(self, **kwargs):
        "set attenuation"
        self.attenuation = kwargs["vec"]

    def setColor(self):
        "Set light source color using coeffs and intensities"
        #
        self.color = QVector3D(
            self.intensity.x() * self.coeffs.x(),
            self.intensity.y() * self.coeffs.y(),
            self.intensity.z() * self.coeffs.z()
        )

    def setIntensity(self, **kwargs):
        "Set channel intensity to val"
        if "vec" in kwargs:
            self.intensity = vec
            self.setColor()
            return

        name = kwargs['channel']
        val = kwargs['val']
        assert val >= 0.0 and val <= 255.0
        name = name.lower()
        if name == "red" or name == "r":
            self.intensity.setX(val)
        elif name == "green" or name == "g":
            self.intensity.setY(val)
        elif name == "blue" or name == "b":
            self.intensity.setZ(val)
        else:
            mess = "Unknown channel name " + name
            mess += ", available channels are: "
            mess += "red, green, blue"
            raise ValueError(mess)
        self.setColor()

    def setCoeffs(self, **kwargs):
        "Set coefficient to given intesity"
        if "vec" in kwargs:
            self.coeffs = kwargs['vec']
            self.setColor()
            return
        name = kwargs['channel']
        val = kwargs['val']
        assert val >= 0.0 and val <= 1.0
        name = name.lower()
        if name == "red" or name == "r":
            self.coeffs.setX(val)
        elif name == "green" or name == "g":
            self.coeffs.setY(val)
        elif name == "blue" or name == "b":
            self.coeffs.setZ(val)
        else:
            mess = "Unknown channel name " + name
            mess += ", available channels are: "
            mess += "red, green, blue"
            raise ValueError(mess)
        self.setColor()

    def getCoeffAverage(self):
        "get average value for coefficients"
        red, green = self.coeffs.x(), self.coeffs.y()
        blue = self.coeffs.z()
        return (red + green + blue) / 3

    def setPosition(self, **kwargs):
        "position as vector"
        if 'vec' in kwargs:
            self.position = kwargs['vec']
            return
        x, y, z = kwargs['x'], kwargs['y'], kwargs['z']
        self.position = QVector3D(x, y, z)

    def setDirection(self, **kwargs):
        "direction"
        if "vec" in kwargs:
            self.direction = kwargs['vec']
            return
        x, y, z = kwargs['x'], kwargs['y'], kwargs['z']
        self.direction = QVector3D(x, y, z)

    def fromPureLightSource(self, light: PureLightSource):
        ""
        self.setPosition(**light.position)
        self.setDirection(**light.direction)
        self.setIntensity("r", light.intensity['r'])
        self.setIntensity("g", light.intensity['g'])
        self.setIntensity("b", light.intensity['b'])
        self.setAttenuation(light.attenConst,
                            light.attenLinear,
                            light.attenQuad)
        self.setCoeffs("r", light.coeffs["r"])
        self.setCoeffs("g", light.coeffs["g"])
        self.setCoeffs("b", light.coeffs["b"])
        self.cutOff = light.cutOff

    def toPureLightSource(self):
        ""
        light = PureLightSource()
        light.setPosition(x=self.position.x(),
                          y=self.position.y(),
                          z=self.position.z())
        light.setDirection(x=self.direction.x(),
                           y=self.direction.y(),
                           z=self.direction.z())
        light.setCutOff(self.cutOff)
        light.setAttenuation(aConst=self.attenuation.x(),
                             aLin=self.attenuation.y(),
                             aQuad=self.attenuation.z())
        light.setCoeffs(channel='r', val=self.coeffs.x())
        light.setCoeffs(channel='g', val=self.coeffs.y())
        light.setCoeffs(channel='b', val=self.coeffs.z())
        light.setIntensity(channel="r", val=self.intensity.x())
        light.setIntensity(channel="g", val=self.intensity.y())
        light.setIntensity(channel="b", val=self.intensity.z())
        return light


class PureLambertianReflector:
    "Object that computes lambertian reflection"

    def __init__(self, lightSource: PureLightSource,
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
                 lightSource: PureLightSource,
                 ambientLight: PureLightSource,
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


class PureShaderLight:
    "Shader light object for illumination"

    def __init__(self,
                 posx=0.0,
                 posy=1.0,
                 posz=0.0,
                 dirx=0.0,
                 diry=-1.0,
                 dirz=-0.1,
                 attenuationConstant=1.0,
                 attenuationLinear=0.7,
                 attenuationQuadratic=1.8,
                 cutOff=math.cos(math.radians(12.5)),
                 ambient=PureLightSource(),
                 diffuse=PureLightSource(),
                 specular=PureLightSource()):
        ""
        self.position = {"x": posx,
                         "y": posy,
                         "z": posz}
        self.direction = {"x": dirx,
                          "y": diry,
                          "z": dirz}
        self.attenConst = attenuationConstant
        self.attenLinear = attenuationLinear
        self.attenQuad = attenuationQuadratic
        self.ambient = ambient
        diffuse.setPosition(x=posx, y=posy, z=posz)
        diffuse.setDirection(x=dirx, y=diry, z=dirz)
        diffuse.setAttenuation(
            aConst=attenuationConstant,
            aLin=attenuationLinear,
            aQuad=attenuationQuadratic)
        self.diffuse = diffuse
        specular.setPosition(x=posx, y=posy, z=posz)
        specular.setDirection(x=dirx, y=diry, z=dirz)
        specular.setAttenuation(
            aConst=attenuationConstant,
            aLin=attenuationLinear,
            aQuad=attenuationQuadratic)
        self.specular = specular
        self.cutOff = cutOff
        self.specular.setCutOff(cutOff)
        self.diffuse.setCutOff(cutOff)

    def getPosition(self):
        return (self.position["x"],
                self.position["y"],
                self.position["z"])

    def setPosition(self, **kwargs):
        "set position"
        x, y, z = kwargs['x'], kwargs['y'], kwargs['z']
        self.position = {"x": x, "y": y, "z": z}
        self.diffuse.setPosition(**kwargs)
        self.specular.setPosition(**kwargs)

    def getDirection(self):
        return (self.direction["x"],
                self.direction["y"],
                self.direction["z"])

    def setDirection(self, **kwargs):
        ""
        x, y, z = kwargs['x'], kwargs['y'], kwargs['z']
        self.direction = {"x": x, "y": y, "z": z}
        self.diffuse.setDirection(**kwargs)
        self.specular.setDirection(**kwargs)

    def getSpecularColor(self):
        return (self.specular.color["r"],
                self.specular.color["g"],
                self.specular.color["b"])

    def getAmbientColor(self):
        return (self.ambient.color["r"],
                self.ambient.color["g"],
                self.ambient.color["b"])

    def getDiffuseColor(self):
        return (self.diffuse.color["r"],
                self.diffuse.color["g"],
                self.diffuse.color["b"])

    def getCutOff(self):
        return self.cutOff

    def setCutOff(self, val: float):
        ""
        self.cutOff = math.cos(math.radians(val))
        self.diffuse.setCutOff(val)
        self.specular.setCutOff(val)

    def setIntensity(self,
                     colorType="all",
                     **kwargs):
        ""
        colorType = colorType.lower()
        if colorType == "specular":
            self.specular.setIntensity(**kwargs)
        elif colorType == "diffuse":
            self.diffuse.setIntensity(**kwargs)
        elif colorType == "all":
            self.diffuse.setIntensity(**kwargs)
            self.specular.setIntensity(**kwargs)
        else:
            mess = "Unknown color type " + colorType
            mess += " known types are specular diffuse"
            raise ValueError(mess)

    def setCoeffs(self, colorType="all",
                  **kwargs):
        "Set intensity coefficients"
        colorType = colorType.lower()
        if colorType == "specular":
            self.specular.setCoeffs(**kwargs)
        elif colorType == "diffuse":
            self.diffuse.setCoeffs(**kwargs)
        elif colorType == "all":
            self.specular.setCoeffs(**kwargs)
            self.diffuse.setCoeffs(**kwargs)
        else:
            mess = "Unknown color type " + colorType
            mess += " known types are specular, diffuse, all"
            raise ValueError(mess)

    def setAttenuation(self, colorType="all",
                       **kwargs):
        ""
        colorType = colorType.lower()
        if colorType == "specular":
            self.specular.setAttenuation(**kwargs)
        elif colorType == "diffuse":
            self.diffuse.setAttenuation(**kwargs)
        elif colorType == "all":
            self.specular.setAttenuation(**kwargs)
            self.diffuse.setAttenuation(**kwargs)
        else:
            mess = "Unknown color type " + colorType
            mess += " known types are specular, diffuse, all"
            raise ValueError(mess)

    def __str__(self):
        "string representation"
        mess = "Shader Light:\n position {0},\n direction {1},\n ambient {2}"
        mess += ",\n diffuse {3},\n specular {4},\n cut off {5}"
        mess += ",\n attenuation constant {6},\n attenuation linear {7}"
        mess += ",\n attenuation quadratic {8}"
        return mess.format(str(self.position), str(self.direction),
                           str(self.ambient), str(self.diffuse),
                           str(self.specular), str(self.cutOff),
                           str(self.attenConst), str(self.attenLinear),
                           str(self.attenQuad))


class QtShaderLight(PureShaderLight):
    "Qt shader light object"

    def __init__(self,
                 position=QVector3D(0.0, 1.0, 0.0),
                 direction=QVector3D(0.0, -1.0, -0.1),
                 cutOff=math.cos(math.radians(12.5)),
                 attenuation=QVector3D(1.0, 0.7, 1.8),
                 ambient=QtLightSource(),
                 diffuse=QtLightSource(),
                 specular=QtLightSource()):
        ""
        super().__init__(
            posx=position.x(),
            posy=position.y(),
            posz=position.z(),
            dirx=direction.x(),
            diry=direction.y(),
            dirz=direction.z(),
            cutOff=cutOff,
            attenuationConstant=attenuation.x(),
            attenuationLinear=attenuation.y(),
            attenuationQuadratic=attenuation.z(),
            ambient=ambient.toPureLightSource(),
            diffuse=QtLightSource().toPureLightSource(),
            specular=QtLightSource().toPureLightSource()
        )
        self.position = position
        self.direction = direction
        self.cutOff = cutOff
        self.ambient = ambient
        #
        self.diffuse = diffuse
        self.diffuse.setPosition(vec=position)
        self.diffuse.setDirection(vec=direction)
        self.diffuse.setAttenuation(vec=attenuation)
        self.diffuse.setCutOff(cutOff)
        #
        self.specular = specular
        self.specular.setPosition(vec=position)
        self.specular.setDirection(vec=direction)
        self.specular.setAttenuation(vec=attenuation)
        self.specular.setCutOff(cutOff)
        #
        self.attenuation = attenuation

    def setPosition(self, **kwargs):
        ""
        self.position = kwargs['vec']
        self.diffuse.setPosition(**kwargs)
        self.specular.setPosition(**kwargs)

    def setDirection(self, **kwargs):
        ""
        self.direction = kwargs['vec']
        self.diffuse.setDirection(**kwargs)
        self.specular.setDirection(**kwargs)

    def getDiffuseColor(self):
        ""
        return self.diffuse.color

    def getAmbientColor(self):
        ""
        return self.ambient.color

    def getSpecularColor(self):
        ""
        return self.specular.color

    def getPosition(self):
        ""
        return self.position

    def getDirection(self):
        ""
        return self.direction
