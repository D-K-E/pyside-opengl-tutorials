# author: Kaan Eraslan
# some util functions

import numpy as np

from PySide2.QtGui import QVector3D
from PySide2.QtGui import QVector4D
from PySide2.QtGui import QMatrix4x4


def normalize_1d_array(arr):
    "Normalize 1d array"
    assert arr.ndim == 1
    result = None
    if np.linalg.norm(arr) == 0:
        result = arr
    else:
        result = arr / np.linalg.norm(arr)
    return result


def normalize_tuple(vec: tuple):
    "Normalize 1 d tuple"
    vecSum = sum([v ** 2 for v in vec])
    if vecSum == 0:
        return vec
    else:
        return tuple([v/vecSum for v in vec])


def crossProduct(vec1, vec2):
    "take cross products of two vectors"
    assert len(vec1) == 3 and len(vec2) == 3
    vec3x = vec1[1] * vec2[2] - vec1[2] * vec2[1]
    vec3y = vec1[2] * vec2[0] - vec1[0] * vec2[2]
    vec3z = vec1[0] * vec2[1] - vec1[1] * vec2[0]
    return (vec3x, vec3y, vec3z)


def vec2vecDot(vec1, vec2):
    "vector to vector dot product"
    assert len(vec1) == len(vec2)
    return tuple(
        sum(v1*v2 for v1, v2 in zip(vec1, vec2))
    )


def sliceCol(colInd: int, matrix):
    "slice column values from matrix"
    rownb = len(matrix)
    return [matrix[i, colInd] for i in range(rownb)]


def mat2matDot(mat1: list, mat2: list):
    "Dot product in pure python"
    assert len(mat1[0]) == len(mat2)
    colnb = len(mat1[0])
    mat = []
    for rown in range(len(mat1)):
        newmatRow = []
        mat1Row = mat1[rown]
        for coln in range(colnb):
            mat2col = sliceCol(coln, mat2)
            newmatRow.append(
                vec2vecDot(mat1Row, mat2col)
            )
        mat.append(newmatRow)
    return mat


def scalar2vecMult(vec, scalar):
    "scalar multiplication of a vector"
    return tuple([v * scalar for v in vec])


def vec2vecAdd(vec1, vec2):
    "vector to vector addition"
    assert len(vec1) == len(vec2)
    return tuple(
        [vec1[i]+vec2[i] for i in range(len(vec1))]
    )


def vec2vecSubs(vec1, vec2):
    "vector to vector subtraction"
    assert len(vec1) == len(vec2)
    return tuple(
        [vec1[i]-vec2[i] for i in range(len(vec1))]
    )


def computeLookAtPure(pos: tuple,
                      center: tuple,
                      up: tuple):
    ""


def computePerspectiveNp(fieldOfView: float,
                         aspect: float,
                         zNear: float, zFar: float):
    "Reproduces glm perspective function"
    assert aspect != 0
    assert zNear != zFar
    fieldOfViewRad = np.radians(fieldOfView)
    fieldHalfTan = np.tan(fieldOfViewRad / 2)
    # mat4
    result = np.zeros((4, 4), dtype=float)
    result[0, 0] = 1 / (aspect * fieldHalfTan)
    result[1, 1] = 1 / fieldHalfTan
    result[2, 2] = -(zFar + zNear) / (zFar - zNear)
    result[3, 2] = -1
    result[2, 3] = -(2 * zFar * zNear) / (zFar - zNear)
    return result


def computePerspectiveQt(fieldOfView: float,
                         aspect: float,
                         zNear: float, zFar: float):
    "matrice"
    mat = QMatrix4x4(*[0.0 for i in range(16)])
    return mat.perspective(fieldOfView,
                           aspect,
                           zNear, zFar)


def computeLookAtPure(pos: tuple,
                      target: tuple,
                      worldUp: tuple):
    ""
    assert len(pos) == 3 and len(target) == 3
    assert len(worldUp) == 3
    zaxis = normalize_tuple(vec2vecSubs(pos, target))

    # x axis
    normWorld = normalize_tuple(worldUp)
    xaxis = normalize_tuple(crossProduct(normWorld,
                                         zaxis))
    yaxis = crossProduct(zaxis, xaxis)
    translation = [
        [1 for i in range(4)] for k in range(4)
    ]
    translation[0][3] = -pos[0]
    translation[1][3] = -pos[1]  # third col, second row
    translation[2][3] = -pos[2]

    rotation = [
        [1 for i in range(4)] for k in range(4)
    ]
    rotation[0][0] = xaxis[0]
    rotation[0][1] = xaxis[1]
    rotation[0][2] = xaxis[2]
    rotation[1][0] = yaxis[0]
    rotation[1][1] = yaxis[1]
    rotation[1][2] = yaxis[2]
    rotation[2][0] = zaxis[0]
    rotation[2][1] = zaxis[1]
    rotation[2][2] = zaxis[2]
    return mat2matDot(translation, rotation)


def computeLookAtMatrixNp(position: np.ndarray,
                          target: np.ndarray,
                          worldUp: np.ndarray):
    "Compute a look at matrix for given position and target"
    assert position.ndim == 1 and target.ndim == 1 and worldUp.ndim == 1
    zaxis = normalize_1d_array(position - target)

    # positive xaxis at right
    xaxis = normalize_1d_array(np.cross(
        normalize_1d_array(worldUp), zaxis)
    )
    # camera up
    yaxis = np.cross(zaxis, xaxis)

    # compute translation matrix
    translation = np.ones((4, 4), dtype=np.float)
    translation[0, 3] = -position[0]  # third col, first row
    translation[1, 3] = -position[1]  # third col, second row
    translation[2, 3] = -position[2]

    # compute rotation matrix
    rotation = np.ones((4, 4), dtype=np.float)
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


def computeLookAtMatrixQt(position: np.ndarray,
                          target: np.ndarray,
                          up: np.ndarray):
    "look at matrice"
    eye = QVector3D(position[0],
                    position[1],
                    position[2])
    target = QVector3D(target[0],
                       target[1],
                       target[2])
    upvec = QVector3D(up[0],
                      up[1],
                      up[2])
    mat4 = QMatrix4x4()
    return mat4.lookAt(eye, target, upvec)


def arr2vec(arr: np.ndarray):
    "convert array 2 vector"
    sqarr = np.squeeze(arr)
    assert sqarr.size == 4
    return QVector4D(sqarr[0],
                     sqarr[1],
                     sqarr[2],
                     sqarr[3])


def arr2qmat(arr: np.ndarray):
    "array to matrix 4x4"
    assert arr.shape == (4, 4)
    mat4 = QMatrix4x4()
    for rowNb in range(arr.shape[0]):
        rowarr = arr[rowNb, :]
        rowvec = arr2vec(rowarr)
        mat4.setRow(rowNb, rowvec)
    #
    return mat4
