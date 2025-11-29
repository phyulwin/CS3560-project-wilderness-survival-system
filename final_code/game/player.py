from core.constants import Direction

class Player:
    """
    Stores stats and components.
    """
    def __init__(self, vision_cls, brain_cls, map_w, map_h):
        sf = 15 + (map_w * .75)
        self.max_strength = sf; self.max_water = sf; self.max_food = sf
        self.current_strength = sf; self.current_water = sf; self.current_food = sf
        self.current_gold = 0
        self.row = 0; self.col = 0
        self.vision = vision_cls()
        self.brain = brain_cls()

    def can_move(self, d, game_map):
        nr = self.row + d[0]; nc = self.col + d[1]
        target = game_map.get_square(nr, nc)
        if not target: return False
        cost = target.terrain
        return (self.current_strength >= cost.movement_cost and
                self.current_water >= cost.water_cost and
                self.current_food >= cost.food_cost)

    def move(self, d, game_map):
        if self.can_move(d, game_map):
            nr = self.row + d[0]; nc = self.col + d[1]
            target = game_map.get_square(nr, nc)
            self.row = nr; self.col = nc
            self.current_strength -= target.terrain.movement_cost
            self.current_water -= target.terrain.water_cost
            self.current_food -= target.terrain.food_cost
            return True
        return False

    def rest(self):
        self.current_strength = min(self.max_strength, self.current_strength + 2)
        self.current_water = max(0, self.current_water - 0.5)
        self.current_food = max(0, self.current_food - 0.5)

    def is_dead(self):
        return (self.current_strength <= 0.1 or self.current_water <= 0.1 or self.current_food <= 0.1)

    def has_won(self, game_map):
        return self.col == game_map.width - 1

    def is_stuck(self, game_map):
        if any(self.can_move(d, game_map) for d in Direction.ALL): return False
        return (self.current_water <= 0.5 or self.current_food <= 0.5)
    