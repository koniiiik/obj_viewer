class Face(tuple):

    def __new__(cls, vertices):
        return tuple.__new__(cls, vertices)

    def get_next_vertex(self, index):
        return self[(index + 1) % len(self)]
