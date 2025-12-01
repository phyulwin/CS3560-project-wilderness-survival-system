"""
Game Session Module - Multi-agent support and world persistence.
"""

import random
import copy
from game.map_grid import Map
from game.player import Player
from game.vision import CautiousVision, KeenEyedVision, FarSightVision, EagleEyeVision
from game.brain import ExplorerBrain, SurvivalistBrain, SmartBrain

VISION_MAP = {
    "Cautious": CautiousVision, "Keen-Eyed": KeenEyedVision,
    "Far-Sight": FarSightVision, "Eagle-Eye": EagleEyeVision
}
BRAIN_MAP = {"Explorer": ExplorerBrain, "Survivalist": SurvivalistBrain, "Smart": SmartBrain}
PLAYER_COLORS = ["#2ecc71", "#3498db", "#e74c3c", "#9b59b6", "#f39c12", "#1abc9c", "#e91e63", "#00bcd4"]


class Agent:
    """Wrapper for a Player entity with metadata for the session."""
    def __init__(self, player, name, vision_name, brain_name, color, start_row, start_col):
        self.player = player
        self.name = name
        self.vision_name = vision_name
        self.brain_name = brain_name
        self.color = color
        self.start_row = start_row
        self.start_col = start_col
        self.is_alive = True
        self.has_won = False

    def reset(self):
        self.player.row = self.start_row
        self.player.col = self.start_col
        self.player.current_strength = self.player.max_strength
        self.player.current_water = self.player.max_water
        self.player.current_food = self.player.max_food
        self.player.current_gold = 0
        self.is_alive = True
        self.has_won = False


class GameSession:
    """Manages game state with multi-player/agent support."""
    
    def __init__(self, account_manager):
        self.account_manager = account_manager
        self.current_user = None
        self.user_data = None
        self.current_world_name = None
        self.game_map = None
        self.initial_map_state = None
        self.players = []  # List of Agent objects
        self.config = None
        self.is_multi_agent = False
        self.lives = 5 # Legacy support
    
    @property
    def player(self):
        """Backward compatibility - returns first player."""
        return self.players[0].player if self.players else None
    
    def get_selected_player(self):
        """Returns the currently selected agent/player."""
        # For now, just return the first one or handle selection logic if needed
        return self.players[0] if self.players else None

    def select_player_at_position(self, row, col):
        """Selects a player if they are at the given coordinates."""
        # Logic to change selection could go here
        return False

    def login(self, username: str, data: dict):
        self.current_user = username
        self.user_data = data
    
    def logout(self):
        if self.current_user and self.current_world_name:
            self.save_world(self.current_world_name)
        self.current_user = None
        self.user_data = None
        self.game_map = None
        self.players = []
        self.config = None
        self.current_world_name = None
    
    def get_world_list(self):
        """Get list of (name, info) tuples for saved worlds."""
        worlds = self.user_data.get("worlds", {}) if self.user_data else {}
        return [(k, v) for k, v in worlds.items()]
    
    def create_world(self, name: str, difficulty: str, width: int, height: int,
                     player_configs: list, is_multi: bool = False) -> bool:
        """Create and save a new world configuration."""
        if not self.user_data or name in self.user_data.get("worlds", {}):
            return False
        
        self.user_data.setdefault("worlds", {})[name] = {
            "difficulty": difficulty, "width": width, "height": height,
            "players": player_configs, "is_multi_agent": is_multi,
            "seed": random.randint(0, 999999)
        }
        self.account_manager.save_progress(self.current_user, self.user_data)
        return True
    
    def load_world(self, name: str) -> bool:
        """Load a saved world and initialize game state."""
        worlds = self.user_data.get("worlds", {})
        if name not in worlds:
            return False
        
        w = worlds[name]
        self.current_world_name = name
        self.is_multi_agent = w.get("is_multi_agent", False)
        self.config = {"difficulty": w["difficulty"], "w": w["width"], "h": w["height"]}
        
        # Generate map
        random.seed(w.get("seed", 0))
        self.game_map = Map(w["width"], w["height"], w["difficulty"])
        self._save_initial_map()
        random.seed()
        
        # Create players
        self.players = []
        for i, pc in enumerate(w.get("players", [])):
            vis_cls = VISION_MAP.get(pc.get("vision", "Cautious"), CautiousVision)
            brain_cls = BRAIN_MAP.get(pc.get("brain", "Explorer"), ExplorerBrain)
            p = Player(vis_cls, brain_cls, w["width"], w["height"])
            p.col = 0
            p.row = self._spawn_row(i, w["height"], len(w["players"]))
            
            # Restore stats if saved
            if "stats" in pc:
                s = pc["stats"]
                p.current_strength = s.get("str", p.max_strength)
                p.current_water = s.get("water", p.max_water)
                p.current_food = s.get("food", p.max_food)
                p.current_gold = s.get("gold", 0)
                p.row, p.col = s.get("row", p.row), s.get("col", p.col)
            
            agent = Agent(
                p, 
                pc.get("name", f"Agent {i+1}"),
                pc.get("vision", "Cautious"),
                pc.get("brain", "Explorer"),
                pc.get("color", PLAYER_COLORS[i % len(PLAYER_COLORS)]),
                p.row, 0
            )
            # If loading from save, we might need to update start_row if it was dynamic, 
            # but for now we assume start pos is fixed or we don't track it strictly for reset 
            # unless we save it. Let's assume reset goes back to spawn.
            agent.start_row = self._spawn_row(i, w["height"], len(w["players"]))
            
            self.players.append(agent)
            
        return True
    
    def _spawn_row(self, idx: int, height: int, total: int) -> int:
        if total == 1:
            return height // 2
        return (height // (total + 1)) * (idx + 1)
    
    def _save_initial_map(self):
        """Store initial map state for reset."""
        if not self.game_map:
            return
        self.initial_map_state = [
            [copy.deepcopy(sq.items) for sq in row]
            for row in self.game_map.squares
        ]
    
    def save_world(self, name: str):
        """Save current world state."""
        if not self.user_data or name not in self.user_data.get("worlds", {}):
            return
        
        w = self.user_data["worlds"][name]
        updated = []
        for agent in self.players:
            p = agent.player
            updated.append({
                "name": agent.name, "vision": agent.vision_name, "brain": agent.brain_name,
                "color": agent.color,
                "stats": {
                    "str": p.current_strength, "water": p.current_water,
                    "food": p.current_food, "gold": p.current_gold,
                    "row": p.row, "col": p.col
                }
            })
        w["players"] = updated
        self.account_manager.save_progress(self.current_user, self.user_data)
    
    def delete_world(self, name: str) -> bool:
        if self.user_data and name in self.user_data.get("worlds", {}):
            del self.user_data["worlds"][name]
            self.account_manager.save_progress(self.current_user, self.user_data)
            return True
        return False
    
    def reset_level(self):
        """Reset all players and restore map."""
        for agent in self.players:
            agent.reset()
        
        if self.initial_map_state and self.game_map:
            for r, row in enumerate(self.initial_map_state):
                for c, items in enumerate(row):
                    self.game_map.squares[r][c].items = copy.deepcopy(items)
    
    def run_turn(self, log_callback=None):
        """Execute one turn for all active players. Returns dict of results."""
        from core.constants import Direction
        from game.trader import Trader
        
        result = {"traders_encountered": [], "deaths": [], "victories": [], "game_over": False, "all_won": False}
        active = [a for a in self.players if a.is_alive and not a.has_won]
        
        if not active:
            result["game_over"] = True
            result["all_won"] = all(a.has_won for a in self.players)
            return result
        
        for agent in active:
            p, m = agent.player, self.game_map
            d = p.brain.make_move(p, p.vision, m)
            
            if d == Direction.STAY:
                p.rest()
                if log_callback: log_callback(f"[{agent.name}] rests.")
            else:
                if p.move(d, m):
                    if log_callback: log_callback(f"[{agent.name}] moves.")
                else:
                    if log_callback: log_callback(f"[{agent.name}] blocked.")
            
            sq = m.get_square(p.row, p.col)
            if sq:
                for item in list(sq.items):
                    if isinstance(item, Trader):
                        result["traders_encountered"].append((agent, item, sq))
                        continue
                    item.on_collect(p, lambda msg: log_callback(f"[{agent.name}] {msg}") if log_callback else None)
                    if not item.is_repeating:
                        sq.items.remove(item)
            
            if p.has_won(m):
                agent.has_won = True
                result["victories"].append(agent)
                if log_callback: log_callback(f"[{agent.name}] WON!")
            elif p.is_dead() or p.is_stuck(m):
                agent.is_alive = False
                result["deaths"].append(agent)
                if log_callback: log_callback(f"[{agent.name}] died!")
        
        if all(not a.is_alive or a.has_won for a in self.players):
            result["game_over"] = True
            result["all_won"] = all(a.has_won for a in self.players)
            
        return result
