class Face(tuple):

    def __new__(cls, vertices):
        return tuple.__new__(cls, vertices)
