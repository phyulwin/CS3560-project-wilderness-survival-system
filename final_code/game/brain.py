import abc
import random
from core.constants import Direction

class Brain(abc.ABC):
    """
    Decides moves.
    """
    @abc.abstractmethod
    def make_move(self, player, vision, game_map): pass

class ExplorerBrain(Brain):
    def make_move(self, p, v, m):
        if p.can_move(Direction.EAST, m): return Direction.EAST
        dirs = Direction.ALL[:]
        random.shuffle(dirs)
        for d in dirs:
            if p.can_move(d, m): return d
        return Direction.STAY

class SurvivalistBrain(Brain):
    def make_move(self, p, v, m):
        if p.current_water < p.max_water / 2:
            path = v.closestWater(m, p)
            if path and path.moves: return path.moves[0]
        if p.current_food < p.max_food / 2:
            path = v.closestFood(m, p)
            if path and path.moves: return path.moves[0]
        return ExplorerBrain().make_move(p, v, m)

class SmartBrain(Brain):
    def make_move(self, p, v, m):
        if p.current_food < p.max_food * .4:
            path = v.closestFood(m, p)
            if path and path.moves: return path.moves[0]
        if p.current_water < p.max_water * .4:
            path = v.closestWater(m, p)
            if path and path.moves: return path.moves[0]
        if p.can_move(Direction.EAST, m): return Direction.EAST
        dirs = Direction.ALL[:]
        random.shuffle(dirs)
        for d in dirs:
            if p.can_move(d, m): return d
        return Direction.STAY