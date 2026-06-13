class Viewpoint:
    __slots__ = ['x', 'y', 'z']

    def __init__(self, x: float, y: float, z: float):
        """
        Initialize the Viewpoint.
        :param x: Camera offset along horizontal direction
        :param y: Camera offset along vertical direction
        :param z: Scale/zoom multiplier
        """
        self.x = x
        self.y = y
        self.z = z

