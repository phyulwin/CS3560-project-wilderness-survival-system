import abc
import random
import sys
import os

# --- PATH FIX ---
current_dir = os.path.dirname(os.path.abspath(__file__)) 
parent_dir = os.path.dirname(current_dir) 
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# --- IMPORTS ---
from core.constants import Direction
# We need to check item types to avoid the "Trader Loop"
from game.items import FoodBonus, WaterBonus, GoldBonus

# Abstract base class
class Brain(abc.ABC):
    @abc.abstractmethod
    def make_move(self, player, vision, game_map): pass
    
    # 1. Prevent death by exhaustion
    def check_fatigue(self, player):
        if player.current_strength < 5:
            return True
        return False

    # 2. Look for items in immediate neighbors
    def check_nearby_items(self, p, m):
        dirs = Direction.ALL[:4]
        random.shuffle(dirs)
        
        for d in dirs:
            nr, nc = p.row + d[0], p.col + d[1]
            sq = m.get_square(nr, nc)
            
            # FIX: Only move for Bonuses (Food/Water/Gold), NOT Traders.
            # Moving for Traders causes infinite loops (Step On -> Step Off -> See Trader -> Step On)
            if sq and p.can_move(d, m):
                for item in sq.items:
                    if isinstance(item, (FoodBonus, WaterBonus, GoldBonus)):
                        return d
        return None

# Simple brain
class ExplorerBrain(Brain):
    def make_move(self, p, v, m):
        if self.check_fatigue(p): return Direction.STAY
        
        loot_dir = self.check_nearby_items(p, m)
        if loot_dir: return loot_dir

        if p.can_move(Direction.EAST, m): return Direction.EAST
        
        dirs = Direction.ALL[:]
        random.shuffle(dirs)
        for d in dirs:
            if p.can_move(d, m): return d
            
        return Direction.STAY

# Survivalist
class SurvivalistBrain(Brain):
    def make_move(self, p, v, m):
        if self.check_fatigue(p): return Direction.STAY

        loot_dir = self.check_nearby_items(p, m)
        if loot_dir: return loot_dir

        if p.current_water < p.max_water * 0.8:
            path = v.closestWater(m, p)
            if path and path.moves:
                move = path.moves[0]
                if p.can_move(move, m): return move
                else: return Direction.STAY 
        
        if p.current_food < p.max_food * 0.8:
            path = v.closestFood(m, p)
            if path and path.moves:
                move = path.moves[0]
                if p.can_move(move, m): return move
                else: return Direction.STAY 
            
        return ExplorerBrain().make_move(p, v, m)

# Smart
class SmartBrain(Brain):
    def make_move(self, p, v, m):
        if self.check_fatigue(p): return Direction.STAY

        loot_dir = self.check_nearby_items(p, m)
        if loot_dir: return loot_dir

        if p.current_food < p.max_food * 0.6:
            path = v.closestFood(m, p)
            if path and path.moves:
                move = path.moves[0]
                if p.can_move(move, m): return move
                else: return Direction.STAY 
            
        if p.current_water < p.max_water * 0.6:
            path = v.closestWater(m, p)
            if path and path.moves:
                move = path.moves[0]
                if p.can_move(move, m): return move
                else: return Direction.STAY 
            
        if p.can_move(Direction.EAST, m): return Direction.EAST
        
        dirs = Direction.ALL[:]
        random.shuffle(dirs)
        for d in dirs:
            if p.can_move(d, m): return d
            
        return Direction.STAY