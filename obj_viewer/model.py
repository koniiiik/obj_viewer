from obj_viewer.errors import WrongFileFormatError
from obj_viewer.matrices import Point
from obj_viewer.face import Face


class Model():
    """Main class handling object creation and manipulation.

    Key attributes:
    vertices -- model's vertices are recorded in this list as
                instances of the Point class; their order is
                significant (see below)
    faces    -- a list containing Faces (tuples) of vertex indices
                (starting at 0) joined by edges, e.g. [[0, 3, 5],
                [1, 2, 6, 8]] means that there are 2 faces: one
                is triangular (with edges between vertices indexed
                0-3, 3-5, 5-0), the latter consists of four edges
                connecting 1 and 2, 2 and 6, 6 and 8, 8 and 1
    """

    def __init__(self, filename):
        self.vertices = []
        self.faces = []
        self.load_from_file(filename)

    def __str__(self):
        pass

    def load_from_file(self, filename):
        """Load the object from an .obj file. Only examine vertices
        ('v') and faces ('f'). Reindex the vertices in faces so that
        they start at 0, not at 1.

        If any error occurs (IOError while opening the file, wrong
        file format), propagate it so that it can be taken care of in
        the right context.
        """

        try:
            source = open(filename)
        except IOError:
            sys.stderr.write('There was a problem opening the input file.')
            raise
        for line in source:
            # Load all of the vertices:
            if line.startswith('v'):
                try:
                    self.vertices.append(Point(*[float(coordinate) for
                                                 coordinate in
                                                 line[2:].rstrip('\n').split()]))
                except TypeError:
                    raise WrongFileFormatError('Invalid input file: '
                                               'unexpected file '
                                               'format.')
            # Load the faces:
            elif line.startswith('f'):
                try:
                    self.faces.append(Face([int(vertex) - 1 for
                                            vertex in
                                            line[2:].rstrip('\n').split()]))
                except IndexError:
                    raise WrongFileFormatError('Invalid input file: '
                                               'face defined before '
                                               'all of its vertices.')
                except TypeError:
                    raise WrongFileFormatError('Invalid input file: '
                                               'unexpected file '
                                               'format.')

        print('A total of %d vertices and %d faces has been loaded.'
              % (len(self.vertices), len(self.faces)))

    def get_x(self, vertex):
        return self.vertices[vertex].get_x()

    def get_y(self, vertex):
        return self.vertices[vertex].get_y()

    def get_z(self, vertex):
        return self.vertices[vertex].get_z()
