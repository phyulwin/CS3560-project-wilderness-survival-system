import abc
import random
from core.constants import Direction

# Abstract base class for decision-making brains.
class Brain(abc.ABC):
    """
    Decides moves.
    """
    # Decide and return the next move for the player (must be implemented by subclasses).
    @abc.abstractmethod
    def make_move(self, player, vision, game_map): pass

# Simple brain that prefers moving east, otherwise random available direction.
class ExplorerBrain(Brain):
    # Return the chosen direction for exploration.
    def make_move(self, p, v, m):
        if p.can_move(Direction.EAST, m): return Direction.EAST
        dirs = Direction.ALL[:]
        random.shuffle(dirs)
        for d in dirs:
            if p.can_move(d, m): return d
        return Direction.STAY

# Prioritizes getting water and food when low, otherwise explores.
class SurvivalistBrain(Brain):
    # Choose move to nearest water/food if needed, else explore.
    def make_move(self, p, v, m):
        if p.current_water < p.max_water / 2:
            path = v.closestWater(m, p)
            if path and path.moves: return path.moves[0]
        if p.current_food < p.max_food / 2:
            path = v.closestFood(m, p)
            if path and path.moves: return path.moves[0]
        return ExplorerBrain().make_move(p, v, m)

# More cautious brain that seeks food/water at higher thresholds then explores east.
class SmartBrain(Brain):
    # Select next move based on resource thresholds and exploration.
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