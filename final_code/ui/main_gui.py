import tkinter as tk
from tkinter import messagebox, font, simpledialog, ttk
import random
import winsound
import threading
import math
import sys
import os
import traceback

# --- PATH SETUP ---
current_ui_folder = os.path.dirname(os.path.abspath(__file__)) 
project_root = os.path.dirname(current_ui_folder) 
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- IMPORTS ---
from core.constants import Direction 
from game.trader import Trader 

# --- CLASS: Security Check Terminal (The Trader Window) ---
class TraderTerminal(tk.Toplevel):
    def __init__(self, parent, trader_name, real_user, real_level, cost, on_trade_success):
        super().__init__(parent)
        self.title(f"Security Check - {trader_name}")
        self.geometry("600x480")
        self.configure(bg="#ecf0f1")
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        self.focus_set()
        
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        
        self.real_user = real_user
        self.real_level = real_level
        self.cost = cost
        self.on_trade_success = on_trade_success
        
        self.step = "USERNAME"
        self.attempts = 3
        
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
        
        self.btn_trade = tk.Button(btn_frame, text="Trade", state="disabled", 
                                   bg="#f1c40f", fg="black", font=("Arial", 10, "bold"), 
                                   width=15, command=self.do_trade)
        self.btn_trade.pack(side=tk.LEFT, padx=10)
        
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

        if self.step == "USERNAME":
            if val == self.real_user:
                self.write_log("System: USERNAME MATCH CONFIRMED.", "success")
                self.write_log("Trader: Okay, name matches. Now, what is your current LEVEL?", "trader")
                self.step = "LEVEL"
                self.attempts = 3 
            else:
                self.attempts -= 1
                if self.attempts > 0:
                    self.write_log(f"System: ERROR. Username mismatch. {self.attempts} attempts left.", "err")
                else:
                    self.write_log("Trader: You're an imposter! \n\tGet out of here before I call the Guards!", "err")
                    self.fail_security()

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
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # --- State Variables ---
        self.autoplay_active = False
        self.auto_trade_enabled = tk.BooleanVar(value=False)

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
        
        # Start at Login Screen
        self.show_login_screen()
    
    def on_close(self):
        """Safely handle closing the window via the X button"""
        if self.session.current_user:
            try:
                self.logout()
            except:
                pass 
        self.destroy()

    def setup_layout(self):
        main_frame = tk.Frame(self, bg="#34495e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # --- LEFT AREA CONTAINER (Holds Map OR Setup OR Login) ---
        self.left_container = tk.Frame(main_frame, bg="#ecf0f1")
        self.left_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # The canvas is created but not packed yet
        self.canvas = tk.Canvas(self.left_container, bg="#ecf0f1")
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Motion>", self.on_mouse_hover)
        
        # --- SIDEBAR ---
        self.sidebar = tk.Frame(main_frame, width=280, bg="#34495e") 
        self.sidebar.pack_propagate(False) 
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        title_font = font.Font(family="Helvetica", size=11, weight="bold")
        
        # --- TILE INSPECTION ---
        tk.Label(self.sidebar, text="TILE INSPECTION", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(10, 5))
        
        self.lbl_tile_name = tk.Label(self.sidebar, text="--", font=("Arial", 12, "bold"), fg="white", bg="#34495e")
        self.lbl_tile_name.pack(pady=2)
        
        self.tile_bars = {}
        for res, color, max_val in [("Strength", "#e74c3c", 5), ("Water", "#3498db", 5), ("Food", "#2ecc71", 5)]:
            f = tk.Frame(self.sidebar, bg="#34495e")
            f.pack(fill=tk.X, pady=1, padx=5)
            lbl = tk.Label(f, text=f"{res}: -", fg="#bdc3c7", bg="#34495e", width=8, anchor="w", font=("Arial", 8))
            lbl.pack(side=tk.LEFT)
            cv = tk.Canvas(f, width=120, height=8, bg="#2c3e50", highlightthickness=0)
            cv.pack(side=tk.LEFT, padx=5)
            self.tile_bars[res] = {"lbl": lbl, "canvas": cv, "color": color, "max": max_val}

        tk.Frame(self.sidebar, height=2, bg="#7f8c8d").pack(fill=tk.X, pady=10, padx=10)
        
        # --- GAME INFO ---
        tk.Label(self.sidebar, text="GAME INFO", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(5, 5))
        self.info_vars = {}
        info_frame = tk.Frame(self.sidebar, bg="#34495e")
        info_frame.pack(fill=tk.X, padx=5)
        for k in ["Level", "Difficulty", "Size"]:
            f = tk.Frame(info_frame, bg="#34495e")
            f.pack(side=tk.LEFT, expand=True)
            tk.Label(f, text=k, fg="#bdc3c7", bg="#34495e", font=("Arial", 8)).pack()
            self.info_vars[k] = tk.StringVar(value="-")
            tk.Label(f, textvariable=self.info_vars[k], fg="white", bg="#34495e", font=("Arial", 9, "bold")).pack()

        tk.Frame(self.sidebar, height=2, bg="#7f8c8d").pack(fill=tk.X, pady=10, padx=10)

        # --- PLAYER STATS (CURRENT) ---
        tk.Label(self.sidebar, text="PLAYER STATS", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(5, 5))
        
        self.player_bars = {}
        p_bar_config = [
            ("Strength", "#e74c3c"), 
            ("Water",    "#3498db"), 
            ("Food",     "#2ecc71"), 
            ("Gold",     "#f1c40f"), 
            ("Lives",    "#9b59b6")  
        ]
        
        for key, color in p_bar_config:
            f = tk.Frame(self.sidebar, bg="#34495e")
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
        tk.Label(self.sidebar, text="ACTIONS", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(20, 10))
        
        self.btn_next = tk.Button(self.sidebar, text="Next Turn", command=self.next_turn, state=tk.DISABLED, bg="#ecf0f1")
        self.btn_next.pack(fill=tk.X, padx=10, pady=5)

        self.btn_auto = tk.Button(self.sidebar, text="Start Autoplay", command=self.toggle_autoplay, state=tk.DISABLED, bg="#8e44ad", fg="white")
        self.btn_auto.pack(fill=tk.X, padx=10, pady=5)
        
        # --- Auto Trade Checkbox ---
        chk_auto_trade = tk.Checkbutton(self.sidebar, text="Auto Trade (If enough Gold)", 
                                        variable=self.auto_trade_enabled, 
                                        bg="#34495e", fg="#f1c40f", selectcolor="#2c3e50",
                                        activebackground="#34495e", activeforeground="#f1c40f",
                                        font=("Arial", 9, "bold"))
        chk_auto_trade.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(self.sidebar, text="Reset Level 1", command=self.reset_game, bg="#e74c3c", fg="white").pack(fill=tk.X, padx=10, pady=5)
        
        self.auth_frame = tk.Frame(self.sidebar, bg="#34495e")
        self.auth_frame.pack(fill=tk.X, pady=10)
        self.update_auth_buttons(is_logged_in=False)
        
        tk.Label(self.sidebar, text="LOG", font=title_font, fg="#f1c40f", bg="#34495e").pack(pady=(5, 2))
        self.log_box = tk.Text(self.sidebar, height=10, state=tk.DISABLED, bg="#2c3e50", fg="white", font=("Courier", 8))
        self.log_box.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # --- SCREEN MANAGEMENT HELPERS ---
    def clear_left_container(self):
        """Clears whatever is currently shown in the left main area (Canvas, Setup, Login, etc)."""
        self.canvas.pack_forget() # Hide map
        for widget in self.left_container.winfo_children():
            if widget != self.canvas:
                widget.destroy()

    def show_game_screen(self):
        """Switches to the Map view."""
        self.clear_left_container()
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.btn_next.config(state=tk.NORMAL)
        self.btn_auto.config(state=tk.NORMAL)

    # --- 1. LOGIN SCREEN (Merged into Main Window) ---
    def show_login_screen(self):
        self.clear_left_container()
        self.btn_next.config(state=tk.DISABLED)
        self.btn_auto.config(state=tk.DISABLED)
        
        # Container for centering
        center_box = tk.Frame(self.left_container, bg="#ecf0f1", relief="groove", bd=2)
        center_box.place(relx=0.5, rely=0.5, anchor="center", width=500, height=450)
        
        tk.Label(center_box, text="SYSTEM LOGIN", font=("Arial", 24, "bold"), fg="#2c3e50", bg="#ecf0f1").pack(pady=(40, 30))
        
        f = tk.Frame(center_box, bg="#ecf0f1")
        f.pack(pady=10)
        
        tk.Label(f, text="Username:", font=("Arial", 14), bg="#ecf0f1").grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.ent_login_user = tk.Entry(f, font=("Arial", 14), width=20)
        self.ent_login_user.grid(row=0, column=1, pady=10)
        
        tk.Label(f, text="Password:", font=("Arial", 14), bg="#ecf0f1").grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.ent_login_pass = tk.Entry(f, font=("Arial", 14), width=20, show="*")
        self.ent_login_pass.grid(row=1, column=1, pady=10)
        self.ent_login_pass.bind("<Return>", lambda e: self.perform_login())
        
        tk.Button(center_box, text="LOGIN", bg="#2980b9", fg="white", font=("Arial", 12, "bold"), 
                  width=15, pady=5, command=self.perform_login).pack(pady=20)
        
        tk.Button(center_box, text="Create New Account", bg="#ecf0f1", fg="#7f8c8d", font=("Arial", 10, "underline"), 
                  relief="flat", command=self.show_register_screen).pack()

    def perform_login(self):
        user = self.ent_login_user.get().strip()
        pwd = self.ent_login_pass.get().strip()
        if not user or not pwd:
            messagebox.showerror("Error", "Please enter username and password.")
            return
        
        data, msg = self.session.account_manager.load_account(user, pwd)
        if data:
            self.on_login_success(user, data)
        else:
            messagebox.showerror("Login Failed", msg)

    # --- 2. REGISTER SCREEN (Merged into Main Window) ---
    def show_register_screen(self):
        self.clear_left_container()
        
        center_box = tk.Frame(self.left_container, bg="#ecf0f1", relief="groove", bd=2)
        center_box.place(relx=0.5, rely=0.5, anchor="center", width=500, height=450)
        
        tk.Label(center_box, text="CREATE ACCOUNT", font=("Arial", 24, "bold"), fg="#27ae60", bg="#ecf0f1").pack(pady=(40, 30))
        
        f = tk.Frame(center_box, bg="#ecf0f1")
        f.pack(pady=10)
        
        tk.Label(f, text="New Username:", font=("Arial", 14), bg="#ecf0f1").grid(row=0, column=0, sticky="e", padx=10, pady=10)
        self.ent_reg_user = tk.Entry(f, font=("Arial", 14), width=20)
        self.ent_reg_user.grid(row=0, column=1, pady=10)
        
        tk.Label(f, text="New Password:", font=("Arial", 14), bg="#ecf0f1").grid(row=1, column=0, sticky="e", padx=10, pady=10)
        self.ent_reg_pass = tk.Entry(f, font=("Arial", 14), width=20, show="*")
        self.ent_reg_pass.grid(row=1, column=1, pady=10)
        
        tk.Button(center_box, text="REGISTER", bg="#27ae60", fg="white", font=("Arial", 12, "bold"), 
                  width=15, pady=5, command=self.perform_register).pack(pady=20)
        
        tk.Button(center_box, text="Back to Login", bg="#ecf0f1", fg="#7f8c8d", font=("Arial", 10, "underline"), 
                  relief="flat", command=self.show_login_screen).pack()

    def perform_register(self):
        user = self.ent_reg_user.get().strip()
        pwd = self.ent_reg_pass.get().strip()
        if not user or not pwd:
            messagebox.showerror("Error", "Fields cannot be empty.")
            return
        
        success, msg = self.session.account_manager.create_account(user, pwd)
        if success:
            messagebox.showinfo("Success", "Account created! Please login.")
            self.show_login_screen()
        else:
            messagebox.showerror("Error", msg)

    # --- 3. SETUP SCREEN (Merged into Main Window) ---
    def show_setup_screen(self):
        self.clear_left_container()
        self.btn_next.config(state=tk.DISABLED)
        self.btn_auto.config(state=tk.DISABLED)
        
        center_box = tk.Frame(self.left_container, bg="#ecf0f1", relief="groove", bd=2)
        center_box.place(relx=0.5, rely=0.5, anchor="center", width=550, height=600)
        
        tk.Label(center_box, text="MISSION SETUP", font=("Arial", 26, "bold"), fg="#2c3e50", bg="#ecf0f1").pack(pady=(40, 10))
        tk.Label(center_box, text="Configure your survival parameters", font=("Arial", 14), fg="#7f8c8d", bg="#ecf0f1").pack(pady=(0, 30))
        
        form_frame = tk.Frame(center_box, bg="#ecf0f1")
        form_frame.pack(pady=10, padx=20)
        
        lbl_font = ("Arial", 14, "bold")
        
        # 1. Difficulty
        tk.Label(form_frame, text="Difficulty:", font=lbl_font, bg="#ecf0f1").grid(row=0, column=0, sticky="w", pady=15, padx=10)
        self.setup_diff = tk.StringVar(value="Medium")
        ttk.Combobox(form_frame, textvariable=self.setup_diff, state="readonly", font=("Arial", 12),
                     values=["Easy", "Medium", "Hard"], width=18).grid(row=0, column=1, sticky="e")

        # 2. Vision
        tk.Label(form_frame, text="Vision Type:", font=lbl_font, bg="#ecf0f1").grid(row=1, column=0, sticky="w", pady=15, padx=10)
        self.setup_vis = tk.StringVar(value="Keen-Eyed")
        ttk.Combobox(form_frame, textvariable=self.setup_vis, state="readonly", font=("Arial", 12),
                     values=["Cautious", "Keen-Eyed", "Far-Sight", "Eagle-Eye"], width=18).grid(row=1, column=1, sticky="e")

        # 3. Brain
        tk.Label(form_frame, text="Strategy:", font=lbl_font, bg="#ecf0f1").grid(row=2, column=0, sticky="w", pady=15, padx=10)
        self.setup_brain = tk.StringVar(value="Survivalist")
        ttk.Combobox(form_frame, textvariable=self.setup_brain, state="readonly", font=("Arial", 12),
                     values=["Explorer", "Survivalist", "Smart"], width=18).grid(row=2, column=1, sticky="e")

        # 4. Width
        tk.Label(form_frame, text="Map Width:", font=lbl_font, bg="#ecf0f1").grid(row=3, column=0, sticky="w", pady=15, padx=10)
        self.setup_w = tk.Entry(form_frame, width=20, font=("Arial", 12))
        self.setup_w.insert(0, "20")
        self.setup_w.grid(row=3, column=1, sticky="e")

        # 5. Height
        tk.Label(form_frame, text="Map Height:", font=lbl_font, bg="#ecf0f1").grid(row=4, column=0, sticky="w", pady=15, padx=10)
        self.setup_h = tk.Entry(form_frame, width=20, font=("Arial", 12))
        self.setup_h.insert(0, "15")
        self.setup_h.grid(row=4, column=1, sticky="e")

        tk.Button(center_box, text="START GAME", bg="#27ae60", fg="white", font=("Arial", 14, "bold"), 
                  width=20, pady=10, command=self.on_setup_start).pack(pady=40)

    def on_setup_start(self):
        try:
            w = int(self.setup_w.get())
            h = int(self.setup_h.get())
            if not (15 <= w <= 100) or not (15 <= h <= 100):
                messagebox.showerror("Invalid Input", "Width and Height must be between 15 and 100.")
                return
            
            # Save config
            self.session.lives = 5 
            self.session.set_config(self.setup_diff.get(), self.setup_vis.get(), self.setup_brain.get(), w, h)
            
            # Start
            self.start_game_sequence(level_up=False, reset_lives=True)
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Width and Height must be numbers.")

    def toggle_autoplay(self):
        if self.autoplay_active:
            self.stop_autoplay()
        else:
            self.start_autoplay()

    def start_autoplay(self):
        if not self.session.player: return
        self.autoplay_active = True
        self.btn_auto.config(text="Stop Autoplay", bg="#c0392b")
        self.btn_next.config(state=tk.DISABLED)
        self.loop_autoplay()

    def stop_autoplay(self):
        self.autoplay_active = False
        self.btn_auto.config(text="Start Autoplay", bg="#8e44ad")
        if self.session.player:
            self.btn_next.config(state=tk.NORMAL)

    def loop_autoplay(self):
        if not self.autoplay_active: return
        if not self.session.player or self.session.player.is_dead():
            self.stop_autoplay()
            return
        self.next_turn()
        if self.autoplay_active:
            self.after(300, self.loop_autoplay)

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
            # Buttons now simply toggle the main screen view
            tk.Button(self.auth_frame, text="Login", command=self.show_login_screen, bg="#2ecc71").pack(fill=tk.X, padx=10, pady=5)
            tk.Button(self.auth_frame, text="Create Account", command=self.show_register_screen, bg="#3498db").pack(fill=tk.X, padx=10, pady=5)

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

    # REMOVED OLD POPUP METHODS (show_login, show_create)

    def on_login_success(self, user, data):
        self.session.login(user, data)
        self.update_auth_buttons(is_logged_in=True)
        self.start_game_sequence(level_up=False, reset_lives=False)

    def start_game_sequence(self, level_up, reset_lives=False):
        try:
            # Check if we should load existing progress
            if self.session.config and not level_up and not reset_lives:
                lvl = self.session.user_data.get("level", 1)
                msg = f"Resume Level {lvl} with previous setup?"
                if self.session.lives < 5: msg += f"\n(Lives remaining: {self.session.lives})"
                
                if messagebox.askyesno("Resume Game", msg):
                    # RESUME: Show game screen immediately
                    self.show_game_screen()
                    self.session.start_level(increase_difficulty=False, reset_lives=False)
                    self.update_game_info()
                    self.draw_map()
                    self.update_ui()
                    return
                else:
                    self.session.reset_progress() 
            
            elif self.session.lives <= 0:
                self.session.config = None

            # If no config (or user reset), SHOW SETUP SCREEN
            if not self.session.config:
                self.show_setup_screen()
                return # Wait for user to click Start in setup screen
            
            # If we are here, we are Leveling Up with existing config
            self.show_game_screen()
            self.session.start_level(increase_difficulty=level_up, reset_lives=reset_lives)
            self.update_game_info()
            self.draw_map()
            self.update_ui()
            self.log(f"Started Level {self.session.user_data['level']}")
            
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error Starting Level", f"Failed to start level: {e}")

    def next_turn(self):
        p = self.session.player
        m = self.session.game_map
        if not p or not m: return

        d = p.brain.make_move(p, p.vision, m)
        if d == Direction.STAY:
            p.rest(); self.log("Player rests.")
        else:
            if p.move(d, m): 
                self.log("Player moves.")
            else: 
                # FIX: Force rest if move fails, preventing infinite loops
                p.rest() 
                self.log("Move blocked. Resting...")

        sq = m.get_square(p.row, p.col)
        for item in list(sq.items):
            if isinstance(item, Trader):
                
                trade_cost = 10
                if "Friendly" in item.name:
                    trade_cost = 7
                elif "Greedy" in item.name:
                    trade_cost = 15

                # --- AUTO TRADE LOGIC ---
                if self.auto_trade_enabled.get():
                    if p.current_gold >= trade_cost:
                        p.current_gold -= trade_cost
                        p.current_food = min(p.max_food, p.current_food + 20)
                        p.current_water = min(p.max_water, p.current_water + 20)
                        self.log(f"Auto-Traded with {item.name} (-{trade_cost} G)")
                        
                        if not item.is_repeating: sq.items.remove(item)
                        continue 
                    else:
                        self.log(f"Skipped {item.name} (Not enough Gold for Auto-Trade)")
                        continue 
                # -------------------------

                was_autoplaying = self.autoplay_active
                if was_autoplaying:
                    self.stop_autoplay()
                    self.log("Autoplay paused for Security Check.")

                actual_user = self.session.current_user
                actual_level = self.session.user_data.get("level", 1)

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
                
                if was_autoplaying:
                    self.start_autoplay()
                
                continue 

            item.on_collect(p, self.log)
            if not item.is_repeating: sq.items.remove(item)

        self.draw_map()
        self.update_ui()
        
        if p.has_won(m):
            self.stop_autoplay()
            self.play_sound("win")
            
            # --- MODIFIED VICTORY LOGIC ---
            if messagebox.askyesno("Victory!", "You reached the other side! Next Level?"):
                self.session.advance_level_progress()
                self.start_game_sequence(level_up=True, reset_lives=True)
            else:
                # User declined next level. Ask to reset or logout.
                if messagebox.askyesno("Game Paused", "Do you want to Reset to Level 1?\n(Click 'No' to Save & Logout)"):
                    self.session.reset_progress()
                    self.start_game_sequence(level_up=False, reset_lives=True)
                else:
                    self.logout()
            # ------------------------------
        
        elif p.is_dead() or p.is_stuck(m):
            self.stop_autoplay()
            self.play_sound("lose")
            self.session.lives -= 1
            self.update_ui()
            funny_msg = random.choice(self.funny_sentences)
            self.log("FATAL: " + funny_msg)
            
            # --- MODIFIED LOSS LOGIC START ---
            if self.session.lives > 0:
                title = "You Died!"
                msg = f"{funny_msg}\n\nLives remaining: {self.session.lives}"
                if self.session.lives == 1: title = "FINAL WARNING"
                
                # 1. Ask to retry current level
                if messagebox.askyesno(title, msg + "\nRetry this level?"):
                    self.start_game_sequence(level_up=False, reset_lives=False)
                else:
                    # 2. User said NO to retry. Ask to Reset or Logout.
                    if messagebox.askyesno("Game Paused", "Do you want to Reset to Level 1?\n(Click 'No' to Save & Logout)"):
                        self.session.reset_progress()
                        self.start_game_sequence(level_up=False, reset_lives=True)
                    else:
                        self.logout()
            else:
                # 3. Game Over (0 lives)
                if messagebox.askyesno("GAME OVER", f"You have run out of lives.\n\n{funny_msg}\n\nDo you want to restart at Level 1?"):
                    self.session.reset_progress()
                    self.start_game_sequence(level_up=False, reset_lives=True)
                else:
                    self.logout()
            # --- MODIFIED LOSS LOGIC END ---

    def reset_game(self):
        if messagebox.askyesno("Reset", "Reset to Level 1?"):
            self.session.reset_progress()
            self.start_game_sequence(level_up=False, reset_lives=True)

    def logout(self):
        self.stop_autoplay()
        self.btn_auto.config(state=tk.DISABLED)
        
        self.session.logout()
        self.canvas.delete("all")
        
        # Reset UI to Login Screen
        self.show_login_screen() 
        
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