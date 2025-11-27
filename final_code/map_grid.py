import random
from terrain import Plains, Forest, Mountain, Desert, Swamp
from items import FoodBonus, WaterBonus, GoldBonus
from trader import FriendlyTrader, GreedyTrader  # <--- CHANGED

class Square:
    def __init__(self, terrain):
        self.terrain = terrain
        self.items = []

class Map:
    """Generates the grid."""
    def __init__(self, width, height, difficulty):
        self.width = width
        self.height = height
        self.difficulty = difficulty
        self.squares = [[None for _ in range(width)] for _ in range(height)]
        self.populate_map()

    def get_square(self, r, c):
        return self.squares[r][c] if 0 <= r < self.height and 0 <= c < self.width else None

    def populate_map(self):
        types = [Plains, Forest, Mountain, Desert, Swamp]
        weights = {"Easy":[.5,.2,.1,.1,.1],"Medium":[.3,.3,.2,.1,.1],"Hard":[.1,.2,.4,.1,.2]}[self.difficulty]
        chance = {"Easy":.2,"Medium":.15,"Hard":.1}[self.difficulty]

        for r in range(self.height):
            for c in range(self.width):
                t = random.choices(types, weights=weights, k=1)[0]
                self.squares[r][c] = Square(t())
                
                if random.random() < chance:
                    # <--- CHANGED: Logic to pick specific trader types
                    roll = random.random()
                    if roll < 0.3: item_obj = FoodBonus()
                    elif roll < 0.6: item_obj = WaterBonus()
                    elif roll < 0.8: item_obj = GoldBonus()
                    else:
                        # 50/50 Chance for Friendly or Greedy trader
                        if random.random() < 0.5: item_obj = FriendlyTrader()
                        else: item_obj = GreedyTrader()
                    
                    self.squares[r][c].items.append(item_obj)