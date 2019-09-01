# author: Kaan Eraslan
# abstract class to be implemented as 3d object

from abc import ABC
from abc import abstractmethod


class Simple3dObject(metaclass=ABC):
    "3d object that requires us to implement several methods"

    @abstractmethod
    def updateObjectVectors(self):
        ""
        pass

    @property
    @abstractmethod
    def position(self):
        "object position in world coordinates"
        return (0.0, 0.0, 0.0)

    @property
    @abstractmethod
    def front(self):
        "object front coordinates"
        return (0.0, 0.0, -1.0)

    @property
    @abstractmethod
    def up(self):
        "object up coordinates "
        pass

    @property
    @abstractmethod
    def right(self):
        "object right"
        pass

    @property
    @abstractmethod
    def yaw(self):
        ""
        return -90.0

    @property
    @abstractmethod
    def pitch(self):
        ""
        return 0.0

    @property
    @abstractmethod
    def roll(self):
        ""
        return 1.0

