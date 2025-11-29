class Direction:
    """Direction vectors used for movement."""
    NORTH = (-1, 0); SOUTH = (1, 0); EAST = (0, 1); WEST = (0, -1)
    NORTHEAST = (-1, 1); NORTHWEST = (-1, -1); SOUTHEAST = (1, 1); SOUTHWEST = (1, -1)
    STAY = (0, 0)
    ALL = [NORTH, SOUTH, EAST, WEST, NORTHEAST, NORTHWEST, SOUTHEAST, SOUTHWEST]

class Path:
    """
    Container for move sequences.
    """
    def __init__(self, moves, total_cost):
        self.moves = moves
        self.total_cost = total_cost