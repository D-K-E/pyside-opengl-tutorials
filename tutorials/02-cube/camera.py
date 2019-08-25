# author: Kaan Eraslan
# camera

import numpy as np


class Camera:
    "An abstract camera for 3d movement in world"

    def __init__(self):
        ""
        self.availableMoves = ["forward", "backward", "left", "right"]
        # Camera attributes
        self.position = np.empty((1, 3), dtype=np.float32)
        self.front = np.empty_like(self.position)
        self.up = np.empty_like(self.position)
        self.right = np.empty_like(self.position)
        self.worldUp = np.empty_like(self.position)

        # Euler Angles for rotation
        self.yaw = 0.0
        self.pitch = 0.0

        # camera options
        self.movementSpeed = 0.0
        self.movementSensitivity = 0.0
        self.zoom = 0.0

    @staticmethod
    def normalize_1d_array(arr):
        "Normalize 1d array"
        assert arr.ndim == 1
        result = None
        if np.linalg.norm(arr) == 0:
            result = arr
        else:
            result = arr / np.linalg.norm(arr)
        return result

    def updateCameraVectors(self):
        "Update the camera vectors and compute a new front"
        yawRadian = np.radians(self.yaw)
        yawCos = np.cos(yawRadian)
        pitchRadian = np.radians(self.pitch)
        pitchCos = np.cos(pitchRadian)
        frontX = yawCos * pitchCos
        frontY = np.sin(pitchRadian)
        frontZ = np.sin(yawRadian) * pitchCos
        front = np.array([frontX, frontY, frontZ], dtype=np.float32)
        self.front = self.normalize_1d_array(front)

        self.right = self.normalize_1d_array(np.cross(self.front,
                                                      self.worldUp))
        self.up = self.normalize_1d_array(np.cross(self.right, self.front))

    def move(self, direction: str, deltaTime: float):
        ""
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

    def lookAround(self, xoffset: float, yoffset: float,
                   pitchBound: bool):
        "Look around with camera"
        xoffset *= self.mouseSensitivity
        yoffset *= self.mouseSensitivity
        self.yaw += xoffset
        self.pitch += yoffset

        if pitchBound:
            if self.pitch > 89.9:
                self.pitch = 89.9
            elif self.pitch < -89.9:
                self.pitch = -89.9
        #
        self.updateCameraVectors()

    def zoomInOut(self, yoffset: float, zoomBound=45.0):
        "Zoom with camera"
        if self.zoom >= 1.0 and self.zoom <= zoomBound:
            self.zoom -= yoffset
        elif self.zoom <= 1.0:
            self.zoom = 1.0
        elif self.zoom >= zoomBound:
            self.zoom = zoomBound

    @classmethod
    def compute_lookAt_matrix(cls,
                              position: np.ndarray,
                              target: np.ndarray,
                              worldUp: np.ndarray):
        "Compute a look at matrix for given position and target"
        assert position.ndim == 1 and target.ndim == 1 and worldUp.ndim == 1
        zaxis = cls.normalize_1d_array(position - target)

        # positive xaxis at right
        xaxis = cls.normalize_1d_array(np.cross(
            cls.normalize_1d_array(worldUp), zaxis)
        )
        # camera up
        yaxis = np.cross(zaxis, xaxis)

        # compute translation matrix
        translation = np.ones((4,4), dtype=np.float)
        translation[0, 3] = -position[0] # third col, first row
        translation[1, 3] = -position[1] # third col, second row
        translation[2, 3] = -position[2]

        # compute rotation matrix
        rotation = np.ones((4,4), dtype=np.float)
        rotation[0, 0] = xaxis[0]
        rotation[0, 1] = xaxis[1]
        rotation[0, 2] = xaxis[2]
        rotation[1, 0] = yaxis[0]
        rotation[1, 1] = yaxis[1]
        rotation[1, 2] = yaxis[2]
        rotation[2, 0] = zaxis[0]
        rotation[2, 1] = zaxis[1]
        rotation[2, 2] = zaxis[2]

        return np.dot(translation, rotation)

    def getViewMatrix(self):
        "Obtain view matrix for camera"
        return self.compute_lookAt_matrix(position=self.position,
                                          target=self.position+self.front,
                                          worldUp=self.up)

class FPSCamera(Camera):
    "FPS Camera"
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
        self.position[1] = 0.0  # y val == 0
