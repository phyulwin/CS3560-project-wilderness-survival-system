import tkinter as tk
from tkinter import messagebox, font, simpledialog
import random
import winsound
import threading
import math
from constants import Direction
from ui_components import CustomDropdownDialog
from ui_login import LoginDialog, CreateAccountDialog
from trader import Trader

# --- CLASS: Security Check Terminal ---
class TraderTerminal(tk.Toplevel):
    def __init__(self, parent, trader_name, real_user, real_level, cost, on_trade_success):
        super().__init__(parent)
        self.title(f"Security Check - {trader_name}")
        self.geometry("600x480")
        self.configure(bg="#ecf0f1")
        self.resizable(False, False)
        
        # Lock interaction to this window
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        
        # Handle the "X" button same as "Leave"
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        self.real_user = real_user
        self.real_level = real_level
        self.cost = cost
        self.on_trade_success = on_trade_success
        
        self.step = "USERNAME"
        self.attempts = 3
        
        # UI Elements
        tk.Label(self, text="SECURITY CHECKPOINT", fg="#c0392b", bg="#ecf0f1", 
                 font=("Courier", 16, "bold")).pack(pady=(15, 0))
        tk.Label(self, text=f"Connection: {trader_name}", fg="#2c3e50", bg="#ecf0f1", 
                 font=("Courier", 12, "bold")).pack(pady=(0, 5))

        self.log_box = tk.Text(self, height=14, width=65, state="disabled", 
                               font=("Courier", 10), bg="#fdfefe", relief="sunken", bd=2)
        self.log_box.pack(padx=10, pady=5)
        
        self.log_box.tag_config("sys", foreground="black", font=("Courier", 10, "bold"))
        self.log_box.tag_config("err", foreground="#c0392b") 
        self.log_box.tag_config("success", foreground="#27ae60") 
        self.log_box.tag_config("user", foreground="#2980b9") 
        self.log_box.tag_config("trader", foreground="#d35400") 

        input_frame = tk.Frame(self, bg="#ecf0f1")
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Input:", bg="#ecf0f1", font=("Arial", 10)).pack(side=tk.LEFT)
        self.entry = tk.Entry(input_frame, width=35, font=("Courier", 10))
        self.entry.pack(side=tk.LEFT, padx=5)
        self.entry.bind("<Return>", lambda e: self.process_input()) 
        
        btn_submit = tk.Button(input_frame, text="Submit", command=self.process_input, 
                               bg="#3498db", fg="white", font=("Arial", 9, "bold"))
        btn_submit.pack(side=tk.LEFT)

        btn_frame = tk.Frame(self, bg="#ecf0f1")
        btn_frame.pack(pady=(5, 15))
        
        # --- CHANGED: Removed special characters ---
        self.btn_trade = tk.Button(btn_frame, text="Trade", state="disabled", 
                                   bg="#f1c40f", fg="black", font=("Arial", 10, "bold"), 
                                   width=15, command=self.do_trade)
        self.btn_trade.pack(side=tk.LEFT, padx=10)
        
        # --- LEAVE BUTTON ---
        # --- CHANGED: Removed special characters ---
        tk.Button(btn_frame, text="Leave", bg="#e74c3c", fg="white", 
                  font=("Arial", 10, "bold"), width=12, command=self.destroy).pack(side=tk.LEFT, padx=10)

        self.write_log("System: BIOMETRIC SCAN FAILED.", "sys")
        self.write_log(f"Trader: Hold it! I can't verify your identity.", "trader")
        self.write_log("Trader: Please enter your exact USERNAME to proceed.", "trader")
        self.entry.focus_set()

    def write_log(self, text, tag=None):
        self.log_box.config(state="normal")
        self.log_box.insert(tk.END, text + "\n", tag)
        self.log_box.see(tk.END)
        self.log_box.config(state="disabled")

    def process_input(self):
        val = self.entry.get().strip()
        if not val: return
        self.write_log(f"You: {val}", "user")
        self.entry.delete(0, tk.END)

        # --- LOGIC FOR USERNAME ---
        if self.step == "USERNAME":
            if val == self.real_user:
                self.write_log("System: USERNAME MATCH CONFIRMED.", "success")
                self.write_log("Trader: Okay, name matches. Now, what is your current LEVEL?", "trader")
                self.step = "LEVEL"
                self.attempts = 3 # Reset attempts
            else:
                self.attempts -= 1
                if self.attempts > 0:
                    self.write_log(f"System: ERROR. Username mismatch. {self.attempts} attempts left.", "err")
                else:
                    self.write_log("Trader: You're an imposter! \n\tGet out of here before I call the Guards!", "err")
                    self.fail_security()

        # --- LOGIC FOR LEVEL ---
        elif self.step == "LEVEL":
            try:
                if int(val) == self.real_level:
                    self.write_log("System: IDENTITY VERIFIED. ACCESS GRANTED.", "success")
                    self.write_log(f"Trader: Verified. I offer supplies (+20 Food/Water).", "trader")
                    self.write_log(f"Trader: My price is {self.cost} Gold.", "trader")
                    
                    self.btn_trade.config(state="normal", text=f"Trade ({self.cost} G)")
                    self.entry.config(state="disabled")
                    self.step = "DONE"
                else:
                    raise ValueError
            except ValueError:
                self.attempts -= 1
                if self.attempts > 0:
                    self.write_log(f"System: ERROR. Level mismatch. {self.attempts} attempts left.", "err")
                else:
                    self.write_log("Trader: That's not the right clearance level! Go away!", "err")
                    self.fail_security()

    def fail_security(self):
        self.entry.config(state="disabled")
        self.btn_trade.config(state="disabled")

    def do_trade(self):
        self.btn_trade.config(state="disabled")
        self.on_trade_success(self)


# --- MAIN GUI CLASS ---
class MainGUI(tk.Tk):
    def __init__(self, session):
        super().__init__()
        self.title("Wilderness Survival System")
        self.geometry("1400x900") 
        self.configure(bg="#2c3e50")
        self.session = session
        
        # --- Autoplay State ---
        self.autoplay_active = False

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
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Motion>", self.on_mouse_hover) 
        
        # --- SIDEBAR ---
        sidebar = tk.Frame(main_frame, width=280, bg="#34495e") 
        sidebar.pack_propagate(False) 
        sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        title_font = font.Font(family="Helvetica", size=11, weight="bold")
        
        # --- TILE INSPECTION ---
        tk.Label(sidebar, text="TILE INSPECTION", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(10, 5))
        
        self.lbl_tile_name = tk.Label(sidebar, text="--", font=("Arial", 12, "bold"), fg="white", bg="#34495e")
        self.lbl_tile_name.pack(pady=2)
        
        # Tile Cost Bars
        self.tile_bars = {}
        for res, color, max_val in [("Strength", "#e74c3c", 5), ("Water", "#3498db", 5), ("Food", "#2ecc71", 5)]:
            f = tk.Frame(sidebar, bg="#34495e")
            f.pack(fill=tk.X, pady=1, padx=5)
            lbl = tk.Label(f, text=f"{res}: -", fg="#bdc3c7", bg="#34495e", width=8, anchor="w", font=("Arial", 8))
            lbl.pack(side=tk.LEFT)
            cv = tk.Canvas(f, width=120, height=8, bg="#2c3e50", highlightthickness=0)
            cv.pack(side=tk.LEFT, padx=5)
            self.tile_bars[res] = {"lbl": lbl, "canvas": cv, "color": color, "max": max_val}

        tk.Frame(sidebar, height=2, bg="#7f8c8d").pack(fill=tk.X, pady=10, padx=10)
        
        # --- GAME INFO ---
        tk.Label(sidebar, text="GAME INFO", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(5, 5))
        self.info_vars = {}
        info_frame = tk.Frame(sidebar, bg="#34495e")
        info_frame.pack(fill=tk.X, padx=5)
        for k in ["Level", "Difficulty", "Size"]:
            f = tk.Frame(info_frame, bg="#34495e")
            f.pack(side=tk.LEFT, expand=True)
            tk.Label(f, text=k, fg="#bdc3c7", bg="#34495e", font=("Arial", 8)).pack()
            self.info_vars[k] = tk.StringVar(value="-")
            tk.Label(f, textvariable=self.info_vars[k], fg="white", bg="#34495e", font=("Arial", 9, "bold")).pack()

        tk.Frame(sidebar, height=2, bg="#7f8c8d").pack(fill=tk.X, pady=10, padx=10)

        # --- PLAYER STATS (CURRENT) ---
        tk.Label(sidebar, text="PLAYER STATS", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(5, 5))
        
        self.player_bars = {}
        p_bar_config = [
            ("Strength", "#e74c3c"), 
            ("Water",    "#3498db"), 
            ("Food",     "#2ecc71"), 
            ("Gold",     "#f1c40f"), 
            ("Lives",    "#9b59b6")  
        ]
        
        for key, color in p_bar_config:
            f = tk.Frame(sidebar, bg="#34495e")
            f.pack(fill=tk.X, pady=2, padx=5)
            
            header = tk.Frame(f, bg="#34495e")
            header.pack(fill=tk.X)
            tk.Label(header, text=key, fg="white", bg="#34495e", font=("Arial", 9, "bold")).pack(side=tk.LEFT)
            val_var = tk.StringVar(value="--")
            tk.Label(header, textvariable=val_var, fg="#bdc3c7", bg="#34495e", font=("Arial", 9)).pack(side=tk.RIGHT)
            
            cv = tk.Canvas(f, width=200, height=10, bg="#2c3e50", highlightthickness=0)
            cv.pack(fill=tk.X, pady=(2, 0))
            
            self.player_bars[key] = {"var": val_var, "canvas": cv, "color": color}

        # --- ACTIONS ---
        tk.Label(sidebar, text="ACTIONS", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(20, 10))
        
        self.btn_next = tk.Button(sidebar, text="Next Turn", command=self.next_turn, state=tk.DISABLED, bg="#ecf0f1")
        self.btn_next.pack(fill=tk.X, padx=10, pady=5)

        # --- Autoplay Button ---
        self.btn_auto = tk.Button(sidebar, text="Start Autoplay", command=self.toggle_autoplay, state=tk.DISABLED, bg="#8e44ad", fg="white")
        self.btn_auto.pack(fill=tk.X, padx=10, pady=5)
        # ----------------------------
        
        tk.Button(sidebar, text="Reset Level 1", command=self.reset_game, bg="#e74c3c", fg="white").pack(fill=tk.X, padx=10, pady=5)
        
        self.auth_frame = tk.Frame(sidebar, bg="#34495e")
        self.auth_frame.pack(fill=tk.X, pady=10)
        self.update_auth_buttons(is_logged_in=False)
        
        # Log
        tk.Label(sidebar, text="LOG", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(5, 2))
        self.log_box = tk.Text(sidebar, height=10, state=tk.DISABLED, bg="#2c3e50", fg="white", font=("Courier", 8))
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # --- LOGIC METHODS ---

    # --- Autoplay Logic ---
    def toggle_autoplay(self):
        if self.autoplay_active:
            self.stop_autoplay()
        else:
            self.start_autoplay()

    def start_autoplay(self):
        if not self.session.player: return
        self.autoplay_active = True
        self.btn_auto.config(text="Stop Autoplay", bg="#c0392b")
        self.btn_next.config(state=tk.DISABLED) # Disable manual next while auto is running
        self.loop_autoplay()

    def stop_autoplay(self):
        self.autoplay_active = False
        self.btn_auto.config(text="Start Autoplay", bg="#8e44ad")
        if self.session.player:
            self.btn_next.config(state=tk.NORMAL)

    def loop_autoplay(self):
        if not self.autoplay_active: return
        
        # Stop if player is dead or game map is gone
        if not self.session.player or self.session.player.is_dead():
            self.stop_autoplay()
            return

        # Execute turn
        self.next_turn()

        # Schedule next step if still active (Speed: 300ms)
        if self.autoplay_active:
            self.after(300, self.loop_autoplay)
    # ---------------------------

    def on_mouse_hover(self, event):
        if not self.session.game_map or self.cell_size == 0: return
        c = int((event.x - self.offset_x) // self.cell_size)
        r = int((event.y - self.offset_y) // self.cell_size)
        sq = self.session.game_map.get_square(r, c)
        
        if sq:
            t = sq.terrain
            self.lbl_tile_name.config(text=t.__class__.__name__, fg=t.color)
            self.draw_tile_bar("Strength", t.movement_cost)
            self.draw_tile_bar("Water", t.water_cost)
            self.draw_tile_bar("Food", t.food_cost)
        else:
            self.lbl_tile_name.config(text="--", fg="white")
            for k in self.tile_bars:
                self.tile_bars[k]["lbl"].config(text=f"{k}: -")
                self.tile_bars[k]["canvas"].delete("all")

    def draw_tile_bar(self, res, val):
        w = self.tile_bars[res]
        w["lbl"].config(text=f"{res}: {val}")
        c = w["canvas"]
        c.delete("all")
        width = 120
        fill = min((val / w["max"]) * width, width)
        c.create_rectangle(0, 0, fill, 8, fill=w["color"], width=0)

    def update_ui(self):
        p = self.session.player
        if not p: return
        
        def update_bar(key, current, maximum):
            w = self.player_bars[key]
            curr_disp = math.ceil(current)
            max_disp = math.ceil(maximum) if isinstance(maximum, (int, float)) else maximum
            
            if isinstance(maximum, (int, float)):
                w["var"].set(f"{curr_disp} / {max_disp}")
            else:
                w["var"].set(f"{curr_disp}")
            
            c = w["canvas"]
            c.delete("all")
            canv_w = c.winfo_width()
            if canv_w < 1: canv_w = 200
            
            if maximum and maximum > 0:
                pct = max(0, min(1, current / maximum))
                fill_w = pct * canv_w
                c.create_rectangle(0, 0, fill_w, 10, fill=w["color"], width=0)

        update_bar("Strength", p.current_strength, p.max_strength)
        update_bar("Water", p.current_water, p.max_water)
        update_bar("Food", p.current_food, p.max_food)
        update_bar("Gold", p.current_gold, 100) 
        update_bar("Lives", self.session.lives, 5)

    def draw_map(self):
        self.canvas.delete("all")
        m = self.session.game_map
        p = self.session.player
        if not m: return
        
        canvas_w = self.canvas.winfo_width()
        canvas_h = self.canvas.winfo_height()
        
        if canvas_w < 10 or canvas_h < 10 or m.width == 0: return

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
        
        px = self.offset_x + (p.col * self.cell_size)
        py = self.offset_y + (p.row * self.cell_size)
        pad = self.cell_size * 0.1
        self.canvas.create_oval(px+pad, py+pad, px+self.cell_size-pad, py+self.cell_size-pad, 
                                fill="#2ecc71", outline="#27ae60", width=2)
        # --- CHANGED: Player icon from special character to 'P' ---
        self.canvas.create_text(px+(self.cell_size/2), py+(self.cell_size/2), text="P", font=emoji_font)

    def on_resize(self, event):
        self.draw_map()
        self.update_ui()

    def update_auth_buttons(self, is_logged_in):
        for widget in self.auth_frame.winfo_children():
            widget.destroy()
        if is_logged_in:
            tk.Button(self.auth_frame, text="Logout", command=self.logout, bg="#95a5a6").pack(fill=tk.X, padx=10, pady=5)
        else:
            tk.Button(self.auth_frame, text="Login", command=self.show_login, bg="#2ecc71").pack(fill=tk.X, padx=10, pady=5)
            tk.Button(self.auth_frame, text="Create Account", command=self.show_create, bg="#3498db").pack(fill=tk.X, padx=10, pady=5)

    def update_game_info(self):
        if not self.session.config: return
        lvl = self.session.user_data.get("level", 1)
        diff = self.session.config["difficulty"]
        w, h = self.session.config["w"], self.session.config["h"]
        self.info_vars["Level"].set(str(lvl))
        self.info_vars["Difficulty"].set(diff)
        self.info_vars["Size"].set(f"{w}x{h}")

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
            if self.session.lives < 5: msg += f"\n(Lives remaining: {self.session.lives})"
            
            if not messagebox.askyesno("Resume Game", msg):
                self.session.reset_progress() # Force Reset if they say NO
        
        elif self.session.lives <= 0:
            self.session.config = None

        if not self.session.config:
            self.session.lives = 5 
            lvl = self.session.user_data.get("level", 1)
            diff = CustomDropdownDialog(self, "Difficulty", f"Level {lvl} Difficulty:", ["Easy", "Medium", "Hard"]).result
            if not diff: self.logout(); return
            
            vis = CustomDropdownDialog(self, "Vision", "Choose Vision:", ["Cautious", "Keen-Eyed", "Far-Sight", "Eagle-Eye"]).result
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
        
        # --- Enable Autoplay Button ---
        self.btn_auto.config(state=tk.NORMAL)
        # -----------------------------------

        self.update_game_info()
        self.draw_map()
        self.update_ui()
        self.log(f"Started Level {self.session.user_data['level']}")

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
            if isinstance(item, Trader):
                # --- CHANGED: Check Autoplay status before opening window ---
                was_auto = self.autoplay_active
                if was_auto:
                    self.stop_autoplay()
                    self.log("Autoplay paused for Security Check.")

                actual_user = self.session.current_user
                actual_level = self.session.user_data.get("level", 1)

                trade_cost = 10
                if "Friendly" in item.name:
                    trade_cost = 7
                elif "Greedy" in item.name:
                    trade_cost = 15

                def trade_callback(terminal):
                    if p.current_gold >= trade_cost:
                        p.current_gold -= trade_cost
                        p.current_food = min(p.max_food, p.current_food + 20)
                        p.current_water = min(p.max_water, p.current_water + 20)
                        terminal.write_log(f"System: Trade Successful! (-{trade_cost}G, +20F, +20W)", "success")
                        self.log(f"Traded with {item.name}.")
                        self.after(1500, terminal.destroy)
                        if not item.is_repeating: sq.items.remove(item)
                    else:
                        terminal.write_log("System: TRANSACTION FAILED. INSUFFICIENT FUNDS.", "err")
                        terminal.write_log("Trader: You don't have enough gold!", "err")
                
                term = TraderTerminal(self, item.name, actual_user, actual_level, trade_cost, trade_callback)
                self.wait_window(term)
                
                # --- CHANGED: Resume Autoplay if it was active ---
                if was_auto:
                    self.start_autoplay()
                
                continue 

            item.on_collect(p, self.log)
            if not item.is_repeating: sq.items.remove(item)

        self.draw_map()
        self.update_ui()
        
        if p.has_won(m):
            self.stop_autoplay() # Stop on Win
            self.play_sound("win")
            if messagebox.askyesno("Victory!", "You reached the other side! Next Level?"):
                self.session.advance_level_progress()
                self.start_game_sequence(level_up=True, reset_lives=True)
            else:
                self.logout()
        
        elif p.is_dead() or p.is_stuck(m):
            self.stop_autoplay() # Stop on Death
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
        self.stop_autoplay()
        self.btn_auto.config(state=tk.DISABLED)
        
        self.session.logout()
        self.canvas.delete("all")
        self.btn_next.config(state=tk.DISABLED)
        self.log_box.config(state=tk.NORMAL)
        self.log_box.delete('1.0', tk.END)
        self.log_box.config(state=tk.DISABLED)
        
        for k in self.player_bars:
            self.player_bars[k]["var"].set("--")
            self.player_bars[k]["canvas"].delete("all")
        
        self.lbl_tile_name.config(text="--")
        self.clear_bars()
        self.log("Logged out.")
        self.update_auth_buttons(is_logged_in=False)
        
    def clear_bars(self):
        for k in self.tile_bars:
            self.tile_bars[k]["lbl"].config(text=f"{k}: -")
            self.tile_bars[k]["canvas"].delete("all")