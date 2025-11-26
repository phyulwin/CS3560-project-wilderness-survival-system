import tkinter as tk
from tkinter import messagebox, font, simpledialog
import random
import abc
from collections import deque
import json
import os

# ==========================================
# PART 1: BASIC DATA STRUCTURES
# ==========================================

class Direction:
    """Direction vectors used for movement."""
    NORTH = (-1, 0); SOUTH = (1, 0); EAST = (0, 1); WEST = (0, -1)
    NORTHEAST = (-1, 1); NORTHWEST = (-1, -1); SOUTHEAST = (1, 1); SOUTHWEST = (1, -1)
    STAY = (0, 0)
    ALL = [NORTH, SOUTH, EAST, WEST, NORTHEAST, NORTHWEST, SOUTHEAST, SOUTHWEST]

class Path:
    """Simple container for a move sequence and an associated (optional) cost."""
    def __init__(self, moves, total_cost):
        self.moves = moves
        self.total_cost = total_cost

# ==========================================
# PART 2: TERRAIN TYPES
# ==========================================

class Terrain(abc.ABC):
    """Abstract base for terrain types (movement/water/food costs + color)."""
    def __init__(self, movement_cost, water_cost, food_cost, color):
        self.movement_cost = movement_cost
        self.water_cost = water_cost
        self.food_cost = food_cost
        self.color = color

class Plains(Terrain):
    def __init__(self): super().__init__(1, 1, 1, "#a7c957")

class Forest(Terrain):
    def __init__(self): super().__init__(2, 1, 2, "#386641")

class Mountain(Terrain):
    def __init__(self): super().__init__(4, 2, 1, "#6a707c")

class Desert(Terrain):
    def __init__(self): super().__init__(2, 4, 1, "#f2e8cf")

class Swamp(Terrain):
    def __init__(self): super().__init__(3, 2, 1, "#585123")

# ==========================================
# PART 3: ITEM DEFINITIONS
# ==========================================

class Item(abc.ABC):
    """Base class for items placed on map squares."""
    def __init__(self, is_repeating, symbol):
        self.is_repeating = is_repeating
        self.symbol = symbol

    @abc.abstractmethod
    def on_collect(self, player, gui):
        pass

class FoodBonus(Item):
    def __init__(self, is_repeating=False):
        super().__init__(is_repeating, "F")
        self.amount = random.randint(5, 15)
    def on_collect(self, p, g):
        p.current_food = min(p.max_food, p.current_food + self.amount)
        g.log_message(f"Found {self.amount} food.")

class WaterBonus(Item):
    def __init__(self, is_repeating=False):
        super().__init__(is_repeating, "W")
        self.amount = random.randint(5, 15)
    def on_collect(self, p, g):
        p.current_water = min(p.max_water, p.current_water + self.amount)
        g.log_message(f"Found {self.amount} water.")

class GoldBonus(Item):
    def __init__(self):
        super().__init__(False, "G")
        self.amount = random.randint(1, 10)
    def on_collect(self, p, g):
        p.current_gold += self.amount
        g.log_message(f"Found {self.amount} gold.")

class Trader(Item):
    def __init__(self):
        super().__init__(True, "T")
    def on_collect(self, p, g):
        g.log_message("Player meets a Trader.")
        if p.current_gold >= 5:
            if messagebox.askyesno("Trade", "Trader offers 10 food & 10 water for 5 gold. Accept?"):
                p.current_gold -= 5
                p.current_food = min(p.max_food, p.current_food + 10)
                p.current_water = min(p.max_water, p.current_water + 10)
                g.log_message("Trade successful!")
        else:
            g.log_message("Trader scoffs at your lack of gold.")

# ==========================================
# PART 4: MAP / SQUARE
# ==========================================

class Square:
    """Represents a single cell on the map: its terrain and any items."""
    def __init__(self, terrain):
        self.terrain = terrain
        self.items = []

class Map:
    """Game map containing a grid of Square objects and a population routine."""
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
                terrain_cls = random.choices(types, weights=weights, k=1)[0]
                self.squares[r][c] = Square(terrain_cls())
                if random.random() < chance:
                    item_type = random.choice([FoodBonus, WaterBonus, GoldBonus, Trader])
                    # make Trader rarer (original logic: skip most trader creations)
                    if item_type == Trader and random.random() > .2:
                        continue
                    is_rep = item_type in [FoodBonus, WaterBonus] and random.random() < .2
                    self.squares[r][c].items.append(item_type(is_rep) if item_type in [FoodBonus, WaterBonus] else item_type())

# ==========================================
# PART 5: PLAYER (STATS, MOVEMENT)
# ==========================================

class Player:
    """Player holds stats, position, vision & brain objects."""
    def __init__(self, vision_cls, brain_cls, map_w, map_h):
        sf = 15 + (map_w * .75)
        self.max_strength = sf
        self.max_water = sf
        self.max_food = sf
        self.current_strength = sf
        self.current_water = sf
        self.current_food = sf
        self.current_gold = 0
        self.row = 0
        self.col = 0
        self.vision = vision_cls()
        self.brain = brain_cls()

    def can_move(self, d, game_map):
        nr = self.row + d[0]; nc = self.col + d[1]
        target = game_map.get_square(nr, nc)
        if not target: return False
        cost = {'strength': target.terrain.movement_cost, 'water': target.terrain.water_cost, 'food': target.terrain.food_cost}
        return (self.current_strength >= cost['strength'] and
                self.current_water >= cost['water'] and
                self.current_food >= cost['food'])

    def move(self, d, game_map):
        nr = self.row + d[0]; nc = self.col + d[1]
        target = game_map.get_square(nr, nc)
        if target and self.can_move(d, game_map):
            cost = {'strength': target.terrain.movement_cost, 'water': target.terrain.water_cost, 'food': target.terrain.food_cost}
            self.row = nr; self.col = nc
            self.current_strength -= cost['strength']
            self.current_water -= cost['water']
            self.current_food -= cost['food']
            return True
        return False

    def rest(self):
        self.current_strength = min(self.max_strength, self.current_strength + 2)
        self.current_water = max(0, self.current_water - 0.5)
        self.current_food = max(0, self.current_food - 0.5)

    def is_dead(self):
        threshold = 0.1
        return (self.current_strength <= threshold or
                self.current_water <= threshold or
                self.current_food <= threshold)

    def has_won(self, game_map):
        return self.col == game_map.width - 1

    def is_stuck(self, game_map):
        can_move_any = any(self.can_move(d, game_map) for d in Direction.ALL)
        if can_move_any: return False
        return (self.current_water <= 0.5 or self.current_food <= 0.5)

# ==========================================
# PART 6: VISION (BFS helpers)
# ==========================================

class Vision(abc.ABC):
    """Base vision class with helper BFS to find nearest items."""
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
                    # bound by vision_range
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

# ==========================================
# PART 7: BRAINS (AI for movement)
# ==========================================

class Brain(abc.ABC):
    @abc.abstractmethod
    def make_move(self, player, vision, game_map): pass

class ExplorerBrain(Brain):
    def make_move(self, p, v, m):
        if p.can_move(Direction.EAST, m): return Direction.EAST
        dirs = Direction.ALL[:]
        random.shuffle(dirs)
        for d in dirs:
            if p.can_move(d, m): return d
        return Direction.STAY

class SurvivalistBrain(Brain):
    def make_move(self, p, v, m):
        if p.current_water < p.max_water / 2:
            path = v.closestWater(m, p)
            if path and path.moves: return path.moves[0]
        if p.current_food < p.max_food / 2:
            path = v.closestFood(m, p)
            if path and path.moves: return path.moves[0]
        return ExplorerBrain().make_move(p, v, m)

class SmartBrain(Brain):
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

# ==========================================
# PART 7.5: ACCOUNT MANAGER
# ==========================================

class AccountManager:
    def __init__(self):
        os.makedirs("users", exist_ok=True)

    def create_account(self, username, password):
        path = f"users/{username}.json"
        if os.path.exists(path):
            return False, "Account already exists."

        data = {
            "username": username,
            "password": password,
            "level": 1
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return True, "Account created successfully."

    def load_account(self, username, password):
        path = f"users/{username}.json"
        if not os.path.exists(path):
            return None, "Account does not exist."

        with open(path, "r") as f:
            data = json.load(f)

        if data.get("password") != password:
            return None, "Incorrect password."

        return data, "Login successful."

    def save_progress(self, username, data):
        with open(f"users/{username}.json", "w") as f:
            json.dump(data, f, indent=4)

# ==========================================
# PART 8: UI - Custom dropdown and main GUI
# ==========================================

class CustomDropdownDialog(tk.Toplevel):
    """Small modal dialog that returns a selected option (or None)."""
    def __init__(self, parent, title, prompt, options):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.result = None
        tk.Label(self, text=prompt, font=("Helvetica", 12)).pack(padx=20, pady=10)
        self.selected_option = tk.StringVar(self)
        self.selected_option.set(options[0])
        dropdown = tk.OptionMenu(self, self.selected_option, *options)
        dropdown.pack(padx=20, pady=5)
        ok_button = tk.Button(self, text="OK", command=self.on_ok, width=10)
        ok_button.pack(padx=20, pady=15)
        self.protocol("WM_DELETE_WINDOW", self.on_cancel)
        self.grab_set()
        self.wait_window(self)

    def on_ok(self):
        self.result = self.selected_option.get()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

class WSS_GUI(tk.Tk):
    """Main GUI for Wilderness Survival simulation."""
    def __init__(self):
        super().__init__()
        self.title("Wilderness Survival")
        self.geometry("1200x800")
        self.configure(bg="#2c3e50")
        
        # Game State
        self.game_map = None
        self.player = None
        self.cell_size = 30
        
        # Account system initialization
        self.account_manager = AccountManager()
        self.current_user = None
        self.user_data = None
        
        # Session Configuration (Stores choices like Diff/Size/Brain so we don't ask every time)
        self.session_config = None 
        
        self.setup_ui()
        
        # Start with login screen instead of immediate game
        self.after(100, self.login_screen)

    def setup_ui(self):
        frame = tk.Frame(self, bg="#34495e")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.canvas = tk.Canvas(frame, bg="#ecf0f1", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        sidebar = tk.Frame(frame, width=300, bg="#34495e")
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=5)
        sidebar.pack_propagate(False)

        tf = font.Font(family="Helvetica", size=16, weight="bold")
        lf = font.Font(family="Helvetica", size=11)

        tk.Label(sidebar, text="Player Stats", font=tf, fg="white", bg="#34495e").pack(pady=10)
        self.stats_vars = {"Strength":tk.StringVar(),"Water":tk.StringVar(),"Food":tk.StringVar(),"Gold":tk.StringVar()}
        for n,v in self.stats_vars.items():
            f = tk.Frame(sidebar, bg="#34495e"); f.pack(fill=tk.X,pady=4)
            tk.Label(f, text=f"{n}:", font=lf, fg="#bdc3c7", bg="#34495e").pack(side=tk.LEFT, padx=5)
            tk.Label(f, textvariable=v, font=lf, fg="white", bg="#34495e").pack(side=tk.RIGHT, padx=5)

        cf = tk.Frame(sidebar, bg="#34495e"); cf.pack(pady=20)
        self.next_turn_button = tk.Button(cf, text="Next Turn", command=self.run_turn, font=lf)
        self.next_turn_button.pack(pady=5)
        
        # --- NEW BUTTON: Reset to Level 1 ---
        tk.Button(cf, text="Reset to Level 1", command=self.reset_progress_prompt, font=lf).pack(pady=5)
        tk.Button(cf, text="Logout", command=self.logout_prompt, font=lf).pack(pady=5)

        tk.Label(sidebar, text="Game Log", font=tf, fg="white", bg="#34495e").pack(pady=10)
        self.log_text = tk.Text(sidebar, height=15, state=tk.DISABLED, bg="#2c3e50", fg="white", font=("Courier", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=5)

    def login_screen(self):
        login = tk.Toplevel(self)
        login.title("Login / Create Account")
        login.geometry("300x180")
        login.transient(self)
        tk.Label(login, text="Username").pack(pady=(10,0))
        entry_user = tk.Entry(login); entry_user.pack(padx=10)
        tk.Label(login, text="Password").pack(pady=(8,0))
        entry_pass = tk.Entry(login, show="*"); entry_pass.pack(padx=10)

        def do_login():
            user = entry_user.get().strip()
            pw = entry_pass.get()
            if not user or not pw:
                messagebox.showerror("Error", "Enter username and password.")
                return
            data, msg = self.account_manager.load_account(user, pw)
            if data:
                self.current_user = user
                self.user_data = data
                messagebox.showinfo("Login", "Login successful.")
                login.destroy()
                self.setup_new_game(level_up=False) # Start game
            else:
                messagebox.showerror("Error", msg)

        def do_create():
            user = entry_user.get().strip()
            pw = entry_pass.get()
            if not user or not pw:
                messagebox.showerror("Error", "Enter username and password.")
                return
            ok, msg = self.account_manager.create_account(user, pw)
            if ok:
                messagebox.showinfo("Account", msg + " You can now login.")
            else:
                messagebox.showerror("Error", msg)

        btn_frame = tk.Frame(login)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Login", command=do_login, width=10).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Create Account", command=do_create, width=12).grid(row=0, column=1, padx=5)

        login.grab_set()
        self.wait_window(login)

    def logout_prompt(self):
        if not self.current_user: return
        if messagebox.askyesno("Logout", "Save progress and logout?"):
            self.account_manager.save_progress(self.current_user, self.user_data)
            self.current_user = None
            self.user_data = None
            self.game_map = None
            self.player = None
            self.session_config = None # Reset session config on logout
            self.canvas.delete("all")
            self.login_screen()

    def reset_progress_prompt(self):
        """Resets the game to Level 1 and clears session config."""
        if not self.current_user: return
        if messagebox.askyesno("Reset", "Are you sure? This will reset you to Level 1 and let you choose settings again."):
            self.user_data["level"] = 1
            self.session_config = None # Forget old choices so we can pick new ones
            self.account_manager.save_progress(self.current_user, self.user_data)
            self.setup_new_game(level_up=False)

    def setup_new_game(self, level_up=False):
        if not self.current_user: return
        
        current_lvl = self.user_data.get("level", 1)
        
        # If we do NOT have a session config yet, ask the user (First time playing or after Reset)
        if self.session_config is None:
            vision_map = {"Cautious":CautiousVision,"Keen-Eyed":KeenEyedVision,"Far-Sight":FarSightVision}
            brain_map = {"Explorer":ExplorerBrain,"Survivalist":SurvivalistBrain,"Smart":SmartBrain}

            difficulty = CustomDropdownDialog(self,"Difficulty",f"Level {current_lvl}: Choose difficulty:",["Easy","Medium","Hard"]).result
            if not difficulty: return
            vision_str = CustomDropdownDialog(self,"Vision","Choose vision type:",list(vision_map.keys())).result
            if not vision_str: return
            brain_str = CustomDropdownDialog(self,"Brain","Choose brain type:",list(brain_map.keys())).result
            if not brain_str: return

            w = simpledialog.askinteger("Map Size","Enter map width:", initialvalue=25, minvalue=10, maxvalue=100, parent=self)
            if not w: return
            h = simpledialog.askinteger("Map Size","Enter map height:", initialvalue=15, minvalue=10, maxvalue=100, parent=self)
            if not h: return
            
            # Store these choices
            self.session_config = {
                "difficulty": difficulty,
                "vis_cls": vision_map.get(vision_str),
                "brain_cls": brain_map.get(brain_str),
                "vis_name": vision_str,
                "brain_name": brain_str,
                "w": w,
                "h": h
            }
        
        # If leveling up, increase size by 1 unit
        if level_up:
            self.session_config["w"] += 1
            self.session_config["h"] += 1
            
        # Retrieve values from session config
        w = self.session_config["w"]
        h = self.session_config["h"]
        difficulty = self.session_config["difficulty"]
        vc = self.session_config["vis_cls"]
        bc = self.session_config["brain_cls"]
        v_name = self.session_config["vis_name"]
        b_name = self.session_config["brain_name"]

        self.game_map = Map(w, h, difficulty)
        self.player = Player(vc, bc, w, h)
        self.player.col = 0
        self.player.row = random.randint(0, self.game_map.height - 1)

        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete('1.0', tk.END)
        self.log_text.config(state=tk.DISABLED)

        self.log_message(f"Level {current_lvl}: {w}x{h} ({difficulty})")
        self.log_message(f"Player: {v_name}, {b_name}")

        self.next_turn_button.config(state=tk.NORMAL)
        self.draw_map()
        self.update_stats()

    def draw_map(self):
        self.canvas.delete("all")
        if not self.game_map: return
        for r in range(self.game_map.height):
            for c in range(self.game_map.width):
                sq = self.game_map.squares[r][c]
                x1,y1 = c*self.cell_size, r*self.cell_size
                x2,y2 = x1+self.cell_size, y1+self.cell_size
                self.canvas.create_rectangle(x1,y1,x2,y2, fill=sq.terrain.color, outline="#2c3e50")
                if sq.items:
                    self.canvas.create_text(x1+self.cell_size/2, y1+self.cell_size/2,
                                             text=sq.items[0].symbol, font=("Helvetica",12,"bold"), fill="black")
        if self.player:
            x1,y1 = self.player.col*self.cell_size, self.player.row*self.cell_size
            x2,y2 = x1+self.cell_size, y1+self.cell_size
            self.canvas.create_oval(x1+4, y1+4, x2-4, y2-4, fill="blue", outline="white", width=2)

    def update_stats(self):
        if self.player:
            self.stats_vars["Strength"].set(f"{self.player.current_strength:.1f}/{self.player.max_strength}")
            self.stats_vars["Water"].set(f"{self.player.current_water:.1f}/{self.player.max_water}")
            self.stats_vars["Food"].set(f"{self.player.current_food:.1f}/{self.player.max_food}")
            self.stats_vars["Gold"].set(str(self.player.current_gold))

    def log_message(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def run_turn(self):
        if not self.player:
            return

        # Immediate checks
        if self.player.is_dead():
            self.check_game_over(); return
        if self.player.is_stuck(self.game_map):
            self.log_message("Player cannot move anywhere!")
            self.check_game_over(); return
        if self.player.has_won(self.game_map):
            self.check_game_over(); return

        # Decide & execute move
        d = self.player.brain.make_move(self.player, self.player.vision, self.game_map)
        if d == Direction.STAY:
            self.player.rest()
            self.log_message("Player rests")
        else:
            if not self.player.move(d, self.game_map):
                self.log_message("Move failed")
            else:
                self.log_message(f"Player moves to ({self.player.row},{self.player.col})")

        # Collect items
        sq = self.game_map.get_square(self.player.row, self.player.col)
        if sq and sq.items:
            for i in list(sq.items):
                i.on_collect(self.player, self)
                if not i.is_repeating:
                    if i in sq.items:
                        sq.items.remove(i)

        self.draw_map()
        self.update_stats()
        self.check_game_over()

    def check_game_over(self):
        if self.player.has_won(self.game_map):
            self.log_message("VICTORY")
            self.next_turn_button.config(state=tk.DISABLED)
            
            # --- VICTORY LOGIC: MOVE UP LEVEL ---
            if messagebox.askyesno("Victory", "You passed! Save progress and setup next level?"):
                self.user_data["level"] = self.user_data.get("level", 1) + 1
                self.account_manager.save_progress(self.current_user, self.user_data)
                # Pass level_up=True so we increase size +1 and skip questions
                self.setup_new_game(level_up=True)
            else:
                self.account_manager.save_progress(self.current_user, self.user_data)
        
        elif self.player.is_dead() or self.player.is_stuck(self.game_map):
            self.log_message("GAME OVER")
            self.next_turn_button.config(state=tk.DISABLED)
            
            # --- DEFEAT LOGIC: REPLAY LEVEL ---
            if messagebox.askyesno("Game Over", "You lost. Replay current level?"):
                # Pass level_up=False so we keep size/diff/brain same and skip questions
                self.setup_new_game(level_up=False)
            else:
                self.account_manager.save_progress(self.current_user, self.user_data)

# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":
    app = WSS_GUI()
    app.mainloop()