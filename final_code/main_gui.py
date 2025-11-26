import tkinter as tk
from tkinter import messagebox, font, simpledialog
import random
import winsound
import threading
from constants import Direction
from ui_components import CustomDropdownDialog
from ui_login import LoginDialog, CreateAccountDialog

class MainGUI(tk.Tk):
    def __init__(self, session):
        super().__init__()
        self.title("Wilderness Survival System")
        self.geometry("1400x900") 
        self.configure(bg="#2c3e50")
        self.session = session
        
        # Map display variables
        self.cell_size = 30
        self.offset_x = 0
        self.offset_y = 0
        
        self.funny_sentences = [
            "You mistook a sleeping bear for a bean bag chair.",
            "You forgot to drink water and turned into a raisin.",
            "The squirrels formed a union and evicted you from the forest.",
            "You walked into a tree... respectfully.",
            "A badger stole your lunch and your dignity.",
            "You tried to pet a wolf. It was a 1/10 experience.",
            "Gravity: 1, You: 0. Watch that cliff next time!",
            "You ate the purple berries. Never eat the purple berries.",
            "You ran out of energy and decided to become a lawn ornament.",
            "The wilderness looked at your survival skills and laughed."
        ]

        self.setup_layout()

    def setup_layout(self):
        main_frame = tk.Frame(self, bg="#34495e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- CANVAS (Map) ---
        self.canvas = tk.Canvas(main_frame, bg="#ecf0f1")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind events
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Motion>", self.on_mouse_hover) 
        
        # --- SIDEBAR ---
        sidebar = tk.Frame(main_frame, width=250, bg="#34495e")
        sidebar.pack_propagate(False) 
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        title_font = font.Font(family="Helvetica", size=12, weight="bold")
        
        # --- TILE INSPECTION ---
        tk.Label(sidebar, text="TILE INSPECTION", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(10, 5))
        
        # Tile Name Label
        self.lbl_tile_name = tk.Label(sidebar, text="--", font=("Arial", 14, "bold"), fg="white", bg="#34495e")
        self.lbl_tile_name.pack(pady=5)
        
        # Cost Bars Container
        self.cost_bars = {}
        # UPDATED LABELS: Strength (Red), Water (Blue), Food (Green)
        bar_configs = [
            ("Strength", "#e74c3c", 5), # Red
            ("Water",    "#3498db", 5), # Blue
            ("Food",     "#2ecc71", 5)  # Green
        ]
        
        for res, color, max_val in bar_configs:
            f = tk.Frame(sidebar, bg="#34495e")
            f.pack(fill=tk.X, pady=2, padx=10)
            
            # Text Label
            lbl = tk.Label(f, text=f"{res}: -", fg="white", bg="#34495e", width=10, anchor="w", font=("Arial", 9))
            lbl.pack(side=tk.LEFT)
            
            # Visual Bar (Canvas)
            cv = tk.Canvas(f, width=100, height=12, bg="#2c3e50", highlightthickness=0)
            cv.pack(side=tk.LEFT, padx=5)
            
            self.cost_bars[res] = {"lbl": lbl, "canvas": cv, "color": color, "max": max_val}

        # --- SEPARATOR ---
        tk.Frame(sidebar, height=2, bg="#7f8c8d").pack(fill=tk.X, pady=15, padx=10)
        
        # --- GAME INFO ---
        tk.Label(sidebar, text="GAME INFO", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(5, 5))
        self.info_vars = {}
        for k in ["Level", "Difficulty", "Size"]:
            frame = tk.Frame(sidebar, bg="#34495e")
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=k, fg="white", bg="#34495e", anchor="w").pack(side=tk.LEFT, padx=10)
            self.info_vars[k] = tk.StringVar(value="--")
            tk.Label(frame, textvariable=self.info_vars[k], fg="#bdc3c7", bg="#34495e", anchor="e").pack(side=tk.RIGHT, padx=10)

        # --- PLAYER STATS ---
        tk.Label(sidebar, text="PLAYER STATS", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(20, 5))
        self.stats = {}
        for k in ["Strength", "Water", "Food", "Gold", "Lives"]:
            frame = tk.Frame(sidebar, bg="#34495e")
            frame.pack(fill=tk.X, pady=2)
            tk.Label(frame, text=k, fg="white", bg="#34495e", anchor="w").pack(side=tk.LEFT, padx=10)
            self.stats[k] = tk.StringVar(value="--")
            tk.Label(frame, textvariable=self.stats[k], fg="#bdc3c7", bg="#34495e", anchor="e").pack(side=tk.RIGHT, padx=10)

        # --- ACTIONS ---
        tk.Label(sidebar, text="ACTIONS", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(20, 10))
        
        self.btn_next = tk.Button(sidebar, text="Next Turn", command=self.next_turn, state=tk.DISABLED, bg="#ecf0f1")
        self.btn_next.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(sidebar, text="Reset Level 1", command=self.reset_game, bg="#e74c3c", fg="white").pack(fill=tk.X, padx=10, pady=5)
        
        # Auth Frame
        self.auth_frame = tk.Frame(sidebar, bg="#34495e")
        self.auth_frame.pack(fill=tk.X, pady=10)
        self.update_auth_buttons(is_logged_in=False)
        
        # Log
        tk.Label(sidebar, text="LOG", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(10, 5))
        self.log_box = tk.Text(sidebar, height=15, state=tk.DISABLED, bg="#2c3e50", fg="white", font=("Courier", 8))
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # --- MOUSE HOVER LOGIC ---
    def on_mouse_hover(self, event):
        """Detects mouse over map and updates inspection panel."""
        if not self.session.game_map or self.cell_size == 0: return
        
        # Calculate grid coordinates using the saved offsets
        c = int((event.x - self.offset_x) // self.cell_size)
        r = int((event.y - self.offset_y) // self.cell_size)
        
        # Get the square at that location
        sq = self.session.game_map.get_square(r, c)
        
        if sq:
            # 1. Update Name
            t = sq.terrain
            name = t.__class__.__name__ # e.g. "Mountain", "Plains"
            self.lbl_tile_name.config(text=name, fg=t.color)
            
            # 2. Update Bars
            # Note: Terrain 'movement_cost' affects Player 'Strength'
            self.draw_bar("Strength", t.movement_cost)
            self.draw_bar("Water", t.water_cost)
            self.draw_bar("Food", t.food_cost)
        else:
            # Mouse is off-map
            self.lbl_tile_name.config(text="--", fg="white")
            self.clear_bars()

    def draw_bar(self, res, val):
        """Draws a colored rectangle representing cost."""
        widgets = self.cost_bars[res]
        max_val = widgets["max"]
        
        # Update text
        widgets["lbl"].config(text=f"{res}: {val}")
        
        # Draw Bar
        c = widgets["canvas"]
        c.delete("all")
        
        width = 100 # Canvas width
        # Calculate bar length (capped at max width)
        fill_width = min((val / max_val) * width, width)
        
        c.create_rectangle(0, 0, fill_width, 12, fill=widgets["color"], width=0)

    def clear_bars(self):
        """Resets bars to empty state."""
        for res in self.cost_bars:
            self.cost_bars[res]["lbl"].config(text=f"{res}: -")
            self.cost_bars[res]["canvas"].delete("all")

    def on_resize(self, event):
        self.draw_map()

    def update_auth_buttons(self, is_logged_in):
        for widget in self.auth_frame.winfo_children():
            widget.destroy()

        if is_logged_in:
            tk.Button(self.auth_frame, text="Logout", command=self.logout, bg="#95a5a6").pack(fill=tk.X, padx=10, pady=5)
        else:
            tk.Button(self.auth_frame, text="Login", command=self.show_login, bg="#2ecc71").pack(fill=tk.X, padx=10, pady=5)
            tk.Button(self.auth_frame, text="Create Account", command=self.show_create, bg="#3498db").pack(fill=tk.X, padx=10, pady=5)

    def log(self, msg):
        self.log_box.config(state=tk.NORMAL)
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)

    def play_sound(self, sound_type):
        def _sound():
            try:
                if sound_type == "win":
                    winsound.Beep(523, 100); winsound.Beep(659, 100) 
                    winsound.Beep(784, 100); winsound.Beep(1046, 400) 
                elif sound_type == "lose":
                    winsound.Beep(349, 350); winsound.Beep(329, 350) 
                    winsound.Beep(311, 350); winsound.Beep(293, 800) 
            except Exception: pass 
        threading.Thread(target=_sound, daemon=True).start()

    def show_login(self):
        LoginDialog(self, self.session.account_manager, self.on_login_success)

    def show_create(self):
        CreateAccountDialog(self, self.session.account_manager)

    def on_login_success(self, user, data):
        self.session.login(user, data)
        self.update_auth_buttons(is_logged_in=True)
        self.start_game_sequence(level_up=False, reset_lives=False)

    def start_game_sequence(self, level_up, reset_lives=False):
        if self.session.config and not level_up and not reset_lives:
            lvl = self.session.user_data.get("level", 1)
            msg = f"Resume Level {lvl} with previous setup?"
            if self.session.lives < 5:
                msg += f"\n(Lives remaining: {self.session.lives})"
            
            if not messagebox.askyesno("Resume Game", msg):
                self.session.config = None
                self.session.lives = 5
        elif self.session.lives <= 0:
            self.session.config = None

        if not self.session.config:
            self.session.lives = 5 
            lvl = self.session.user_data.get("level", 1)
            diff = CustomDropdownDialog(self, "Difficulty", f"Level {lvl} Difficulty:", ["Easy", "Medium", "Hard"]).result
            if not diff: self.logout(); return
            
            vis = CustomDropdownDialog(self, "Vision", "Choose Vision:", ["Cautious", "Keen-Eyed", "Far-Sight"]).result
            if not vis: self.logout(); return
            
            brain = CustomDropdownDialog(self, "Brain", "Choose Brain:", ["Explorer", "Survivalist", "Smart"]).result
            if not brain: self.logout(); return
            
            w = simpledialog.askinteger("Size", "Width (15-100):", minvalue=15, maxvalue=100)
            if not w: self.logout(); return
            
            h = simpledialog.askinteger("Size", "Height (15-100):", minvalue=15, maxvalue=100)
            if not h: self.logout(); return
            
            self.session.set_config(diff, vis, brain, w, h)
        
        self.session.start_level(increase_difficulty=level_up, reset_lives=reset_lives)
        self.btn_next.config(state=tk.NORMAL)
        self.update_game_info()
        self.draw_map()
        self.update_ui()
        self.log(f"Started Level {self.session.user_data['level']}")

    def update_game_info(self):
        if not self.session.config: return
        lvl = self.session.user_data.get("level", 1)
        diff = self.session.config["difficulty"]
        w, h = self.session.config["w"], self.session.config["h"]
        self.info_vars["Level"].set(str(lvl))
        self.info_vars["Difficulty"].set(diff)
        self.info_vars["Size"].set(f"{w}x{h}")

    def draw_map(self):
        self.canvas.delete("all")
        m = self.session.game_map
        p = self.session.player
        if not m: return
        
        # --- DYNAMIC RESIZING & OFFSET CALCULATION ---
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        if canvas_w < 10 or canvas_h < 10 or m.width == 0 or m.height == 0: return

        cell_w = canvas_w / m.width
        cell_h = canvas_h / m.height
        self.cell_size = min(cell_w, cell_h)
        
        self.offset_x = (canvas_w - (m.width * self.cell_size)) / 2
        self.offset_y = (canvas_h - (m.height * self.cell_size)) / 2
        
        font_size = int(self.cell_size * 0.5)
        if font_size < 8: font_size = 8
        dynamic_font = ("Arial", font_size, "bold")
        emoji_font = ("Segoe UI Emoji", int(self.cell_size * 0.6))

        for r in range(m.height):
            for c in range(m.width):
                sq = m.squares[r][c]
                x1 = self.offset_x + (c * self.cell_size)
                y1 = self.offset_y + (r * self.cell_size)
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=sq.terrain.color, outline="")
                if sq.items:
                    cx = x1 + (self.cell_size / 2)
                    cy = y1 + (self.cell_size / 2)
                    self.canvas.create_text(cx, cy, text=sq.items[0].symbol, font=dynamic_font)
        
        # Draw Player (Ant)
        px = self.offset_x + (p.col * self.cell_size)
        py = self.offset_y + (p.row * self.cell_size)
        pad = self.cell_size * 0.1
        
        self.canvas.create_oval(px+pad, py+pad, px+self.cell_size-pad, py+self.cell_size-pad, 
                                fill="#2ecc71", outline="#27ae60", width=2)
        self.canvas.create_text(px+(self.cell_size/2), py+(self.cell_size/2), text="🐜", font=emoji_font)

    def update_ui(self):
        p = self.session.player
        if not p: return
        self.stats["Strength"].set(f"{p.current_strength:.1f}")
        self.stats["Water"].set(f"{p.current_water:.1f}")
        self.stats["Food"].set(f"{p.current_food:.1f}")
        self.stats["Gold"].set(str(p.current_gold))
        self.stats["Lives"].set(str(self.session.lives))

    def next_turn(self):
        p = self.session.player
        m = self.session.game_map
        
        if not p or not m: return

        d = p.brain.make_move(p, p.vision, m)
        if d == Direction.STAY:
            p.rest(); self.log("Player rests.")
        else:
            if p.move(d, m): self.log("Player moves.")
            else: self.log("Move blocked.")

        sq = m.get_square(p.row, p.col)
        for item in list(sq.items):
            item.on_collect(p, self.log)
            if not item.is_repeating: sq.items.remove(item)

        self.draw_map()
        self.update_ui()
        
        if p.has_won(m):
            self.play_sound("win")
            if messagebox.askyesno("Victory!", "You reached the other side! Next Level?"):
                self.session.advance_level_progress()
                self.start_game_sequence(level_up=True, reset_lives=True)
            else:
                self.logout()
        
        elif p.is_dead() or p.is_stuck(m):
            self.play_sound("lose")
            self.session.lives -= 1
            self.update_ui()
            
            funny_msg = random.choice(self.funny_sentences)
            self.log("FATAL: " + funny_msg)
            
            if self.session.lives > 0:
                title = "You Died!"
                msg = f"{funny_msg}\n\nLives remaining: {self.session.lives}"
                if self.session.lives == 1: title = "FINAL WARNING"
                if messagebox.askyesno(title, msg + "\nRetry this level?"):
                    self.start_game_sequence(level_up=False, reset_lives=False)
                else:
                    self.logout()
            else:
                if messagebox.askyesno("GAME OVER", f"You have run out of lives.\n\n{funny_msg}\n\nDo you want to restart at Level 1?"):
                    self.session.reset_progress()
                    self.start_game_sequence(level_up=False, reset_lives=True)
                else:
                    self.logout()

    def reset_game(self):
        if messagebox.askyesno("Reset", "Reset to Level 1?"):
            self.session.reset_progress()
            self.start_game_sequence(level_up=False, reset_lives=True)

    def logout(self):
        self.session.logout()
        self.canvas.delete("all")
        self.btn_next.config(state=tk.DISABLED)
        
        self.log_box.config(state=tk.NORMAL)
        self.log_box.delete('1.0', tk.END)
        self.log_box.config(state=tk.DISABLED)

        for v in self.stats.values(): v.set("--")
        for v in self.info_vars.values(): v.set("--")
        self.lbl_tile_name.config(text="--")
        self.clear_bars()
        
        self.log("Logged out.")
        self.update_auth_buttons(is_logged_in=False)