from map_grid import Map
from player import Player
# <--- CHANGED: Import the new 4th Vision Type
from vision import CautiousVision, KeenEyedVision, FarSightVision, EagleEyeVision
from brain import ExplorerBrain, SurvivalistBrain, SmartBrain
import random

class GameSession:
    """
    Manages the current active game context and saves/loads state.
    """
    def __init__(self, account_manager):
        self.account_manager = account_manager
        self.current_user = None
        self.user_data = None
        
        self.game_map = None
        self.player = None
        self.lives = 5
        self.config = None

    def login(self, username, data):
        self.current_user = username
        self.user_data = data
        self.lives = data.get("saved_lives", 5)
        if "saved_config" in data:
            self.restore_config(data["saved_config"])

    def logout(self):
        if self.current_user and self.user_data:
            self.user_data["saved_lives"] = self.lives
            if self.config:
                self.user_data["saved_config"] = self.get_serializable_config()
            self.account_manager.save_progress(self.current_user, self.user_data)
        
        self.current_user = None
        self.user_data = None
        self.game_map = None
        self.player = None
        self.config = None
        self.lives = 5

    def get_serializable_config(self):
        if not self.config: return None
        return {
            "difficulty": self.config["difficulty"],
            "vis_name": self.config["vis_name"],
            "brain_name": self.config["brain_name"],
            "w": self.config["w"],
            "h": self.config["h"]
        }

    def restore_config(self, saved_cfg):
        # <--- CHANGED: Added EagleEye to map
        v_map = {
            "Cautious": CautiousVision, 
            "Keen-Eyed": KeenEyedVision, 
            "Far-Sight": FarSightVision,
            "Eagle-Eye": EagleEyeVision
        }
        b_map = {"Explorer":ExplorerBrain, "Survivalist":SurvivalistBrain, "Smart":SmartBrain}
        self.config = saved_cfg.copy()
        self.config["vis_cls"] = v_map.get(saved_cfg["vis_name"], CautiousVision)
        self.config["brain_cls"] = b_map.get(saved_cfg["brain_name"], ExplorerBrain)

    def set_config(self, diff, v_name, b_name, w, h):
        # <--- CHANGED: Added EagleEye to map
        v_map = {
            "Cautious": CautiousVision, 
            "Keen-Eyed": KeenEyedVision, 
            "Far-Sight": FarSightVision,
            "Eagle-Eye": EagleEyeVision
        }
        b_map = {"Explorer":ExplorerBrain, "Survivalist":SurvivalistBrain, "Smart":SmartBrain}
        self.config = {
            "difficulty": diff,
            "vis_cls": v_map[v_name],
            "brain_cls": b_map[b_name],
            "vis_name": v_name,
            "brain_name": b_name,
            "w": w,
            "h": h
        }

    def start_level(self, increase_difficulty=False, reset_lives=False):
        if not self.config: return
        
        if increase_difficulty:
            self.config["w"] += 1
            self.config["h"] += 1
            self.lives = 5 
        elif reset_lives:
            self.lives = 5
            
        w, h = self.config["w"], self.config["h"]
        self.game_map = Map(w, h, self.config["difficulty"])
        self.player = Player(self.config["vis_cls"], self.config["brain_cls"], w, h)
        self.player.col = 0
        self.player.row = random.randint(0, h - 1)

    def advance_level_progress(self):
        self.user_data["level"] = self.user_data.get("level", 1) + 1
        self.user_data["saved_lives"] = self.lives
        if self.config:
            self.user_data["saved_config"] = self.get_serializable_config()
        self.account_manager.save_progress(self.current_user, self.user_data)

    def reset_progress(self):
        self.user_data["level"] = 1
        self.config = None 
        self.lives = 5
        self.account_manager.save_progress(self.current_user, self.user_data)