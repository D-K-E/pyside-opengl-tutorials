# author: Kaan Eraslan
# camera

import numpy as np
import math
from tutorials.utils.utils import computeLookAtPure
from tutorials.utils.utils import normalize_tuple
from tutorials.utils.utils import crossProduct
from tutorials.utils.utils import scalar2vecMult
from tutorials.utils.utils import vec2vecAdd
from tutorials.utils.utils import vec2vecSubs
from tutorials.utils.utils import move3dObjPure
from tutorials.utils.utils import move3dObjQt
from PySide2.QtGui import QVector3D
from PySide2.QtGui import QMatrix4x4
from PySide2.QtGui import QVector4D


class PureCamera:
    "A camera that is in pure python for 3d movement"

    def __init__(self):
        ""
        # camera properties
        self.position = (0.0, 0.0, 0.0)
        self.front = None
        self.worldUp = (0.0, 1.0, 0.0)
        self.up = None
        self.right = None

        # euler angles
        self.yaw = -90.0
        self.pitch = 0.0
        self.roll = 0.0

        # movement speed, sensitivity, moves, zoom
        self.movementSensitivity = 0.001
        self.movementSpeed = 2.5
        self.zoom = 45.0
        self.availableMoves = ["forward",
                               "backward",
                               "left",
                               "right"]

        # update camera vectors
        self.updateCameraVectors()

    def updateCameraVectors(self):
        "Update the camera vectors and compute a new front"
        yawRadian = math.radians(self.yaw)
        yawCos = math.cos(yawRadian)
        pitchRadian = math.radians(self.pitch)
        pitchCos = math.cos(pitchRadian)
        frontX = yawCos * pitchCos
        frontY = math.sin(pitchRadian)
        frontZ = math.sin(yawRadian) * pitchCos
        self.front = (frontX, frontY, frontZ)
        self.front = normalize_tuple(self.front)
        self.right = crossProduct(
            self.front,
            self.worldUp)
        self.right = normalize_tuple(self.right)
        self.up = crossProduct(
            self.right,
            self.front)
        self.up = normalize_tuple(self.up)

    def move(self, direction: str, deltaTime: float):
        ""
        self.position = move3dObjPure(direction=direction,
                                      deltaTime=deltaTime,
                                      positionVector=self.position,
                                      axvec1=self.front,
                                      axvec2=self.right,
                                      availableMoves=self.availableMoves)

    def lookAround(self,
                   xoffset: float,
                   yoffset: float,
                   pitchBound: bool):
        "Look around with camera"
        xoffset *= self.movementSensitivity
        yoffset *= self.movementSensitivity
        self.yaw += xoffset
        self.pitch += yoffset

        if pitchBound:
            if self.pitch > 90.0:
                self.pitch = 90.0
            elif self.pitch < -90.0:
                self.pitch = -90.0
        #
        self.updateCameraVectors()

    def zoomInOut(self, yoffset: float,
                  zoomBound=45.0):
        "Zoom with camera"
        if self.zoom >= 1.0 and self.zoom <= zoomBound:
            self.zoom -= yoffset
        elif self.zoom <= 1.0:
            self.zoom = 1.0
        elif self.zoom >= zoomBound:
            self.zoom = zoomBound

    def setCameraWithVectors(self,
                             position: tuple,
                             up: tuple,
                             front: tuple,
                             yaw: float,
                             pitch: float,
                             zoom: float,
                             speed: float,
                             sensitivity: float):
        "Set camera"
        assert len(position) == len(up)
        assert len(up) == len(front)
        assert len(front) == 3
        self.position = position
        self.worldUp = up
        self.pitch = pitch
        self.yaw = yaw
        self.movementSpeed = speed
        self.movementSensitivity = sensitivity
        self.front = front
        self.zoom = zoom
        self.updateCameraVectors()

    def setCameraWithFloatVals(self,
                               posx: float,
                               posy: float,
                               posz: float,
                               upx: float,
                               upy: float,
                               upz: float,
                               yaw: float,
                               pitch: float,
                               speed: float,
                               sensitivity: float,
                               zoom: float,
                               front: tuple):
        "Set camera floats"
        assert len(front) == 3
        self.position = (posx, posy, posz)
        self.worldUp = (upx, upy, upz)
        self.yaw = yaw
        self.pitch = pitch
        self.movementSpeed = speed
        self.movementSensitivity = sensitivity
        self.zoom = zoom
        self.front = front
        self.updateCameraVectors()

    def getViewMatrix(self):
        "Obtain view matrix for camera"
        return computeLookAtPure(
            pos=self.position,
            target=vec2vecAdd(self.position,
                              self.front),
            worldUp=self.worldUp
        )
    def __str__(self):
        "string representation"
        mess = "Camera: position {0},\n yaw: {1},\n pitch: {2},\n world up:{3}"
        mes = mess.format(str(self.position), str(self.yaw),
                          str(self.pitch), str(self.worldUp)
                          )
        return  mes


class QtCamera:
    "An abstract camera for 3d movement in world"

    def __init__(self):
        ""
        self.availableMoves = ["forward", "backward", "left", "right"]
        # Camera attributes
        self.position = QVector3D(0.0, 0.0, 0.0)
        self.front = QVector3D(0.0, 0.0, -0.5)
        self.worldUp = QVector3D(0.0, 1.0, 0.0)
        self.right = QVector3D()
        self.up = QVector3D()

        # Euler Angles for rotation
        self.yaw = -90.0
        self.pitch = 0.0

        # camera options
        self.movementSpeed = 2.5
        self.movementSensitivity = 0.00001
        self.zoom = 45.0

    def updateCameraVectors(self):
        "Update the camera vectors and compute a new front"
        yawRadian = np.radians(self.yaw)
        yawCos = np.cos(yawRadian)
        pitchRadian = np.radians(self.pitch)
        pitchCos = np.cos(pitchRadian)
        frontX = yawCos * pitchCos
        frontY = np.sin(pitchRadian)
        frontZ = np.sin(yawRadian) * pitchCos
        self.front = QVector3D(frontX, frontY, frontZ)
        self.front.normalize()
        self.right = QVector3D.crossProduct(
            self.front,
            self.worldUp)
        self.right.normalize()
        self.up = QVector3D.crossProduct(
            self.right,
            self.front)
        self.up.normalize()

    def move(self, direction: str, deltaTime: float):
        ""
        self.position = move3dObjQt(
            direction=direction,
            deltaTime=deltaTime,
            speed=self.movementSpeed,
            positionVector=self.position,
            axvec1=self.front,
            axvec2=self.right,
            availableMoves=self.availableMoves
        )

    def lookAround(self,
                   xoffset: float,
                   yoffset: float,
                   pitchBound: bool):
        "Look around with camera"
        xoffset *= self.movementSensitivity
        yoffset *= self.movementSensitivity
        self.yaw += xoffset
        self.pitch += yoffset

        if pitchBound:
            if self.pitch > 89.9:
                self.pitch = 89.9
            elif self.pitch < -89.9:
                self.pitch = -89.9
        #
        self.updateCameraVectors()

    def zoomInOut(self, yoffset: float,
                  zoomBound=45.0):
        "Zoom with camera"
        if self.zoom >= 1.0 and self.zoom <= zoomBound:
            self.zoom -= yoffset
        elif self.zoom <= 1.0:
            self.zoom = 1.0
        elif self.zoom >= zoomBound:
            self.zoom = zoomBound

    def getViewMatrix(self):
        "Obtain view matrix for camera"
        view = QMatrix4x4()
        view.lookAt(self.position,
                    self.position+self.front,
                    self.up
                    )
        return view

    def setCameraWithVectors(self,
                             position=QVector3D(0.0, 0.0, 0.0),
                             worldUp=QVector3D(0.0, 1.0, 0.0),
                             yaw=-90.0,
                             pitch=0.0,
                             zoom=45.0,
                             speed=2.5,
                             sensitivity=0.00001):
        "Set camera"
        self.position = position
        self.worldUp = worldUp
        self.pitch = pitch
        self.yaw = yaw
        self.movementSpeed = speed
        self.movementSensitivity = sensitivity
        self.zoom = zoom
        self.updateCameraVectors()

    def setCameraWithFloatVals(self,
                               posx=0.0,
                               posy=0.0,
                               posz=0.0,
                               upx=0.0,
                               upy=1.0,
                               upz=0.0,
                               yaw=-90.0,
                               pitch=0.0,
                               zoom=45.0,
                               speed=2.5,
                               sensitivity=0.00001,
                               ):
        "Set camera floats"
        self.position = QVector3D(posx, posy, posz)
        self.worldUp = QVector3D(upx, upy, upz)
        self.yaw = yaw
        self.pitch = pitch
        self.movementSpeed = speed
        self.movementSensitivity = sensitivity
        self.zoom = zoom
        self.updateCameraVectors()

    def __str__(self):
        "string representation"
        mess = "Camera: position {0}, yaw: {1}, pitch: {2}, world up:{3}"
        mes = mess.format(str(self.position), str(self.yaw),
                          str(self.pitch), str(self.worldUp)
                          )
        return  mes



class FPSCameraQt(QtCamera):
    "FPS Camera based on qtcamera"

    def __init__(self):
        super().__init__()

    def move(self, direction: str, deltaTime: float):
        "Move camera in single axis"
        velocity = self.movementSpeed * deltaTime
        direction = direction.lower()
        if direction not in self.availableMoves:
            raise ValueError(
                "Unknown direction {0}, available moves are {1}".format(
                    direction, self.availableMoves
                )
            )
        if direction == "forward":
            self.position += self.front * velocity
        elif direction == "backward":
            self.position -= self.front * velocity
        elif direction == "right":
            self.position += self.right * velocity
        elif direction == "left":
            self.position -= self.right * velocity

        self.position.setY(0.0)  # y val == 0
