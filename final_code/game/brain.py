import abc
import random
import sys
import os

# --- PATH FIX: Ensure Python can find 'core' folder ---
# Get the directory containing this file (final_code/game/)
current_dir = os.path.dirname(os.path.abspath(__file__)) 
# Get the project root (final_code/)
project_root = os.path.dirname(current_dir) 

# Add project root to sys.path so we can import 'core'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- CORRECT IMPORT ---
# Directly import from the core folder
from core.constants import Direction

# Abstract base class for decision-making brains.
class Brain(abc.ABC):
    """
    Decide and return the next move for the player.
    """
    @abc.abstractmethod
    def make_move(self, player, vision, game_map): pass
    
    # --- Logic to prevent death by exhaustion ---
    def check_fatigue(self, player):
        # If strength is critically low (less than 5), FORCE a rest.
        if player.current_strength < 5:
            return True
        return False

# Simple brain that prefers moving east, otherwise random available direction.
class ExplorerBrain(Brain):
    def make_move(self, p, v, m):
        # 1. REST if tired
        if self.check_fatigue(p):
            return Direction.STAY
            
        # 2. Try East
        if p.can_move(Direction.EAST, m): return Direction.EAST
        
        # 3. Random valid move
        dirs = Direction.ALL[:]
        random.shuffle(dirs)
        for d in dirs:
            if p.can_move(d, m): return d
            
        return Direction.STAY

# Prioritizes getting water and food when low, otherwise explores.
class SurvivalistBrain(Brain):
    def make_move(self, p, v, m):
        # 1. REST if tired
        if self.check_fatigue(p):
            return Direction.STAY

        # 2. Seek Water if low
        if p.current_water < p.max_water / 2:
            path = v.closestWater(m, p)
            if path and path.moves: return path.moves[0]
        
        # 3. Seek Food if low
        if p.current_food < p.max_food / 2:
            path = v.closestFood(m, p)
            if path and path.moves: return path.moves[0]
            
        # 4. Explore
        return ExplorerBrain().make_move(p, v, m)

# More cautious brain that seeks food/water at higher thresholds.
class SmartBrain(Brain):
    def make_move(self, p, v, m):
        # 1. REST if tired
        if self.check_fatigue(p):
            return Direction.STAY

        # 2. Seek Food (High priority)
        if p.current_food < p.max_food * .4:
            path = v.closestFood(m, p)
            if path and path.moves: return path.moves[0]
            
        # 3. Seek Water (High priority)
        if p.current_water < p.max_water * .4:
            path = v.closestWater(m, p)
            if path and path.moves: return path.moves[0]
            
        # 4. Explore East
        if p.can_move(Direction.EAST, m): return Direction.EAST
        
        # 5. Random fallback
        dirs = Direction.ALL[:]
        random.shuffle(dirs)
        for d in dirs:
            if p.can_move(d, m): return d
            
        return Direction.STAY