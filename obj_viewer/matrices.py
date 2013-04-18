import math

from obj_viewer.errors import IncompatibleMatricesError
from obj_viewer.constants import *


class Matrix(list):
    """Base class for all matrices. Constructs a new matrix either
    by specifying the desired dimensions (creates a new matrix filled
    by zeros) or by transforming a 2D list into one.
    """

    def __init__(self, matrix = None, rows = None, cols = None):
        if matrix is not None:
            super(Matrix, self).__init__(matrix)
            self.rows = len(matrix)
            self.cols = len(matrix[0])
        else:
            if rows is not None and cols is not None:
                super(Matrix, self).__init__([[0 for c in range(cols)]
                                              for r in range(rows)])
                self.rows = rows
                self.cols = cols
            else:
                raise ValueError('Matrix creation failed: Neither a '
                                 'matrix, nor row and column count '
                                 'present in parameters.')

    def transposed(self):
        return Matrix([[row[i] for row in self] for i
                       in range(self.rows)])

    def __mul__(self, matrix):
        if self.cols != matrix.rows:
            raise IncompatibleMatricesError('Matrix multiplication '
                                            'called on matrices of '
                                            'incompatible '
                                            'dimensions.')
        else:
            transposed = matrix.transposed()
            return Matrix([[sum(cell1 * cell2 for cell1, cell2
                            in zip(row, col)) for col
                            in transposed] for row in self])


class Point(Matrix):
    """Class representing points as 1x4 matrices. The first three
    columns hold the x-y-z coordinates of the point; the last
    position is set to 1 for convenient manipulation.
    """

    def __init__(self, x, y, z):
        Matrix.__init__(self, [[x, y, z, 1]])

    def get_view_coordinates(self, transformation_matrix,
                             view_matrix):
        """Calculate the location of the point in the viewport,
        taking into account any transformation that has been applied
        to the model (stored in transformation_matrix).
        """
        new_coordinates = self * transformation_matrix * view_matrix
        return (new_coordinates[0][0], new_coordinates[0][1],
                new_coordinates[0][2])

    def get_x(self):
        return self[0][0]

    def get_y(self):
        return self[0][1]

    def get_z(self):
        return self[0][2]


class Vector(Matrix):
    """Class representing vectors as 1x4 matrices. The first three
    values hold the x-y-z coordinates of the vector; the last position
    is occupied by a 0.
    """

    def __init__(self, x, y, z):
        Matrix.__init__(self, [[x, y, z, 0]])

    def get_x(self):
        return self[0][0]

    def get_y(self):
        return self[0][1]

    def get_z(self):
        return self[0][2]


class Identity(Matrix):
    """Class representing identity matrices; that is, square
    matrices containing ones on the main diagonal and zeros everywhere
    else.
    """

    def __init__(self):
        Matrix.__init__(self, rows = DIMENSIONS + 1,
                        cols = DIMENSIONS + 1)
        for i in range(DIMENSIONS + 1):
            self[i][i] = 1


class Rotation(Matrix):
    """Class capable of creating matrices for rotation around a given
    axis by a specified angle (given in radians or degrees).
    """

    def __init__(self, axis, radians = None, degrees = DEGREES):
        Matrix.__init__(self, rows = DIMENSIONS + 1,
                        cols = DIMENSIONS + 1)
        for i in range(DIMENSIONS + 1):
            self[i][i] = 1
        if radians is not None:
            self.angle = radians
        else:
            self.angle = math.radians(degrees)
        if axis == 'x':
            self.set_rotation_around_x()
        elif axis == 'y':
            self.set_rotation_around_y()
        elif axis == 'z':
            self.set_rotation_around_z()

    def set_rotation_around_x(self):
        sin = math.sin(self.angle)
        cos = math.cos(self.angle)
        self[1][1] = cos
        self[1][2] = -sin
        self[2][1] = sin
        self[2][2] = cos

    def set_rotation_around_y(self):
        sin = math.sin(self.angle)
        cos = math.cos(self.angle)
        self[0][0] = cos
        self[0][2] = sin
        self[2][0] = -sin
        self[2][2] = cos

    def set_rotation_around_z(self):
        sin = math.sin(self.angle)
        cos = math.cos(self.angle)
        self[0][0] = cos
        self[0][1] = sin
        self[1][0] = -sin
        self[1][1] = cos


class Translation(Matrix):
    """Class responsible for translation matrices."""

    def __init__(self, axis, dist):
        Matrix.__init__(self, rows = DIMENSIONS + 1,
                        cols = DIMENSIONS + 1)
        for i in range(DIMENSIONS + 1):
            self[i][i] = 1
        if axis == 'x':
            self[DIMENSIONS][0] = dist
        elif axis == 'y':
            self[DIMENSIONS][1] = dist
        elif axis == 'z':
            self[DIMENSIONS][2] = dist


class Scaling(Matrix):
    """Class handling scaling matrices."""

    def __init__(self, factor):
        Matrix.__init__(self, rows = DIMENSIONS + 1,
                        cols = DIMENSIONS + 1)
        self[0][0] = factor
        self[1][1] = factor
        self[2][2] = factor


class ViewportTransformation(Matrix):
    """Class handling the creation of a viewport transformation
    matrix, that is, a matrix which scales objects to be visible in
    the viewport and moves the origin to the viewport center.
    """

    def __init__(self):
        this = [[VIEW_SCALE,      0,                0, 0],
                [0,               -VIEW_SCALE,      0, 0],
                [0,               0,                1, 0],
                [VIEW_WIDTH // 2, VIEW_HEIGHT // 2, 0, 1]]
        Matrix.__init__(self, this)
