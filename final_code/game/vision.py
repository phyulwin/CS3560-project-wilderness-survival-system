import abc
from collections import deque
from core.constants import Direction, Path
from game.items import FoodBonus, WaterBonus

# Vision scans the surrounding map for items within a limited range.
# Provides generic pathfinding to the nearest item of a given class.
class Vision(abc.ABC):
    """
    Scans for items.
    """
    # Initialize vision with a maximum Manhattan offset.
    # vision_range controls how far the search will explore from the player.
    def __init__(self, vision_range):
        self.vision_range = vision_range

    # Breadth-first search to find the nearest square containing item_class.
    # Returns a Path to that item or None if not found within vision_range.
    def _find_closest_item(self, map_instance, player, item_class):
        q = deque([(player.row, player.col, [])])
        visited = {(player.row, player.col)}
        while q:
            r, c, path = q.popleft()
            sq = map_instance.get_square(r, c)
            if sq and any(isinstance(i, item_class) for i in sq.items) and path:
                return Path(path, {})
            for d in Direction.ALL:
                nr, nc = r + d[0], c + d[1]
                if (nr, nc) not in visited and map_instance.get_square(nr, nc):
                    if abs(nr - player.row) <= self.vision_range and abs(nc - player.col) <= self.vision_range:
                        visited.add((nr, nc))
                        q.append((nr, nc, path + [d]))
        return None

    # Shortcut to find the closest FoodBonus using _find_closest_item.
    # Returns a Path or None.
    def closestFood(self, m, p): return self._find_closest_item(m, p, FoodBonus)
    # Shortcut to find the closest WaterBonus using _find_closest_item.
    # Returns a Path or None.
    def closestWater(self, m, p): return self._find_closest_item(m, p, WaterBonus)

# CautiousVision has very short sight (1 tile).
# Instantiated with vision_range=1 for conservative behavior.
class CautiousVision(Vision):
    def __init__(self): super().__init__(1)

# KeenEyedVision can see slightly further (2 tiles).
# Instantiated with vision_range=2 for improved detection.
class KeenEyedVision(Vision):
    def __init__(self): super().__init__(2)

# FarSightVision has a larger range and a shaped field of view.
# Overrides searching to only include specific visible offsets instead of a rectangle.
class FarSightVision(Vision):
    # Set vision_range to 3 and define a set of visible offsets to model cone-like sight.
    # visible_offsets contains relative (row, col) positions considered visible from the player.
    def __init__(self):
        super().__init__(3)
        self.visible_offsets = {(-2,0),(-1,0),(0,0),(1,0),(2,0),(-1,-1),(0,-1),(1,-1),(-2,1),(-1,1),(0,1),(1,1),(-1,2),(0,2),(1,2)}
    
    # BFS that only expands into squares whose offsets from the player are in visible_offsets.
    # Returns a Path to the nearest matching item within the shaped field of view or None.
    def _find_closest_item(self, map_instance, player, item_class):
        # [cite_start]Override for specific offsets [cite: 141]
        q = deque([(player.row, player.col, [])])
        visited = {(player.row, player.col)}
        while q:
            r, c, path = q.popleft()
            if any(isinstance(i, item_class) for i in map_instance.get_square(r, c).items) and path:
                return Path(path, {})
            for d in Direction.ALL:
                nr, nc = r + d[0], c + d[1]
                offset = (nr - player.row, nc - player.col)
                if (nr, nc) not in visited and map_instance.get_square(nr, nc) and offset in self.visible_offsets:
                    visited.add((nr, nc))
                    q.append((nr, nc, path + [d]))
        return None