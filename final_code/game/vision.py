import abc
from collections import deque
from game.items import FoodBonus, WaterBonus
from core.constants import Path, Direction

class Vision(abc.ABC):
    """
    Base Vision class.
    Defines how far the agent can 'see' to find resources.
    """
    def __init__(self, radius):
        self.radius = radius

    def _find_closest(self, game_map, player, target_type):
        """
        Breadth-First Search (BFS) to find the closest item of target_type.
        """
        start_node = (player.row, player.col)
        queue = deque([(start_node, [])]) # ( (r,c), [moves] )
        visited = set([start_node])
        
        while queue:
            (curr_r, curr_c), path = queue.popleft()
            
            # Check range constraint (Manhattan distance for simplicity)
            dist = abs(curr_r - player.row) + abs(curr_c - player.col)
            if dist > self.radius:
                continue

            # Check if this square has the item we want
            sq = game_map.get_square(curr_r, curr_c)
            if sq:
                for item in sq.items:
                    if isinstance(item, target_type):
                        # Calculate cost (simplified as length of path)
                        return Path(path, len(path))

            # Explore neighbors
            for d in Direction.ALL:
                nr, nc = curr_r + d[0], curr_c + d[1]
                if 0 <= nr < game_map.height and 0 <= nc < game_map.width:
                    if (nr, nc) not in visited:
                        visited.add((nr, nc))
                        # Only add to queue if we assume we can walk there (ignoring cost for vision check)
                        queue.append(((nr, nc), path + [d]))
        return None

    def closestFood(self, game_map, player):
        return self._find_closest(game_map, player, FoodBonus)

    def closestWater(self, game_map, player):
        return self._find_closest(game_map, player, WaterBonus)

# --- 4 Types of Vision (Max Points: 10) ---

class CautiousVision(Vision):
    """Short range, safe play."""
    def __init__(self): super().__init__(3)

class KeenEyedVision(Vision):
    """Medium range."""
    def __init__(self): super().__init__(6)

class FarSightVision(Vision):
    """Long range."""
    def __init__(self): super().__init__(10)

class EagleEyeVision(Vision):
    """
    Infinite range. Sees everything on the map.
    This is the 4th type required for max points.
    """
    def __init__(self): super().__init__(999)