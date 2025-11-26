import abc
from collections import deque
from constants import Direction, Path
from items import FoodBonus, WaterBonus

class Vision(abc.ABC):
    """
    Scans for items.
    """
    def __init__(self, vision_range):
        self.vision_range = vision_range

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

    def closestFood(self, m, p): return self._find_closest_item(m, p, FoodBonus)
    def closestWater(self, m, p): return self._find_closest_item(m, p, WaterBonus)

class CautiousVision(Vision):
    def __init__(self): super().__init__(1)

class KeenEyedVision(Vision):
    def __init__(self): super().__init__(2)

class FarSightVision(Vision):
    def __init__(self):
        super().__init__(3)
        self.visible_offsets = {(-2,0),(-1,0),(0,0),(1,0),(2,0),(-1,-1),(0,-1),(1,-1),(-2,1),(-1,1),(0,1),(1,1),(-1,2),(0,2),(1,2)}
    
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