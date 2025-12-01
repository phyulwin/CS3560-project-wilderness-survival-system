"""
Main GUI Module - Single-window architecture for Wilderness Survival System.

This module implements the main application controller and all screen frames,
replacing the legacy popup-based interface with a modern scene-based approach.
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import winsound
import threading
import math

from core.constants import Direction
from game.trader import Trader
from ui.ui_components import (
    BaseFrame, StatusBar, ScrollableFrame, WorldListItem, 
    AgentConfigRow, OverlayMessage
)


class WildernessSurvivalApp(tk.Tk):
    """
    Main Application Controller.
    Manages the main window and handles frame switching.
    """
    
    def __init__(self, session):
        super().__init__()
        self.session = session
        self.title("Wilderness Survival System")
        self.geometry("1280x800")
        self.configure(bg="#2c3e50")
        
        # Container for frames
        self.container = tk.Frame(self, bg="#2c3e50")
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.current_frame = None
        self.switch_frame(LoginFrame)

    def switch_frame(self, frame_class, **kwargs):
        """Destroys current frame and replaces it with a new one."""
        if self.current_frame:
            self.current_frame.on_hide()
            self.current_frame.destroy()
        
        self.current_frame = frame_class(self.container, self, **kwargs)
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        self.current_frame.on_show()


class LoginFrame(BaseFrame):
    """Screen 1: Login / Welcome Screen."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        # Center content
        center_frame = tk.Frame(self, bg=self.BG_DARK)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        self.create_title_label("WILDERNESS SURVIVAL SYSTEM", size=32).pack(in_=center_frame, pady=20)
        self.create_subtitle_label("Multi-Agent Simulation Edition").pack(in_=center_frame, pady=(0, 30))
        
        # Login Form
        form_frame = tk.Frame(center_frame, bg=self.BG_MEDIUM, padx=40, pady=40)
        form_frame.pack(pady=10)
        
        self.create_label("Username", size=12).pack(in_=form_frame, anchor="w")
        self.user_entry = self.create_entry()
        self.user_entry.pack(in_=form_frame, pady=(5, 15))
        self.user_entry.focus_set()
        
        self.create_label("Password", size=12).pack(in_=form_frame, anchor="w")
        self.pass_entry = self.create_entry(show="*")
        self.pass_entry.pack(in_=form_frame, pady=(5, 25))
        self.pass_entry.bind("<Return>", lambda e: self.login())
        
        # Buttons
        self.create_button("LOGIN", self.login, "success", width=25).pack(in_=form_frame, pady=5)
        self.create_button("CREATE ACCOUNT", self.create_account, "primary", width=25).pack(in_=form_frame, pady=5)

    def login(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get()
        data, msg = self.session.account_manager.load_account(u, p)
        
        if data:
            self.session.login(u, data)
            self.controller.switch_frame(MainMenuFrame)
        else:
            messagebox.showerror("Login Failed", msg)

    def create_account(self):
        self.controller.switch_frame(CreateAccountFrame)


class CreateAccountFrame(BaseFrame):
    """Screen 1.5: Create Account Screen."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        center_frame = tk.Frame(self, bg=self.BG_DARK)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        self.create_title_label("Create Account", size=24).pack(in_=center_frame, pady=20)
        
        form_frame = tk.Frame(center_frame, bg=self.BG_MEDIUM, padx=40, pady=40)
        form_frame.pack(pady=10)
        
        # Username
        self.create_label("Username", size=12).pack(in_=form_frame, anchor="w")
        self.user_entry = self.create_entry()
        self.user_entry.pack(in_=form_frame, pady=(5, 15))
        self.user_entry.focus_set()
        
        # Password
        self.create_label("Password", size=12).pack(in_=form_frame, anchor="w")
        self.pass_entry = self.create_entry(show="*")
        self.pass_entry.pack(in_=form_frame, pady=(5, 15))
        
        # Confirm Password
        self.create_label("Confirm Password", size=12).pack(in_=form_frame, anchor="w")
        self.confirm_entry = self.create_entry(show="*")
        self.confirm_entry.pack(in_=form_frame, pady=(5, 25))
        self.confirm_entry.bind("<Return>", lambda e: self.submit())
        
        # Buttons
        self.create_button("CREATE", self.submit, "success", width=25).pack(in_=form_frame, pady=5)
        self.create_button("BACK", lambda: controller.switch_frame(LoginFrame), "secondary", width=25).pack(in_=form_frame, pady=5)

    def submit(self):
        u = self.user_entry.get().strip()
        p = self.pass_entry.get()
        c = self.confirm_entry.get()
        
        if not u or not p:
            messagebox.showerror("Error", "Username and password required.")
            return
            
        if p != c:
            messagebox.showerror("Error", "Passwords do not match.")
            return
            
        success, msg = self.session.account_manager.create_account(u, p)
        
        if success:
            messagebox.showinfo("Success", "Account created successfully! Please login.")
            self.controller.switch_frame(LoginFrame)
        else:
            messagebox.showerror("Error", msg)


class MainMenuFrame(BaseFrame):
    """Screen 2: Main Menu."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        center_frame = tk.Frame(self, bg=self.BG_DARK)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        user = self.session.current_user
        self.create_title_label(f"Welcome, {user}").pack(in_=center_frame, pady=20)
        
        btn_frame = tk.Frame(center_frame, bg=self.BG_DARK)
        btn_frame.pack(pady=20)
        
        self.create_button("SELECT LEVEL / WORLD", 
                          lambda: controller.switch_frame(LevelSelectionFrame), 
                          "primary", width=30).pack(in_=btn_frame, pady=10)
        
        self.create_button("LOGOUT", self.logout, "danger", width=30).pack(in_=btn_frame, pady=10)

    def logout(self):
        self.session.logout()
        self.controller.switch_frame(LoginFrame)


class LevelSelectionFrame(BaseFrame):
    """Screen 3: Level Selection (Minecraft-style)."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        # Header
        header = tk.Frame(self, bg=self.BG_DARK, height=80)
        header.pack(fill="x", padx=20, pady=20)
        
        self.create_title_label("Select World").pack(in_=header, side="left")
        self.create_button("Back", lambda: controller.switch_frame(MainMenuFrame), 
                          "secondary", width=10).pack(in_=header, side="right")
        
        # World List
        list_container = tk.Frame(self, bg=self.BG_MEDIUM, padx=2, pady=2)
        list_container.pack(fill="both", expand=True, padx=40, pady=20)
        
        self.scroll_frame = ScrollableFrame(list_container)
        self.scroll_frame.pack(fill="both", expand=True)
        
        # Footer Actions
        footer = tk.Frame(self, bg=self.BG_DARK, height=60)
        footer.pack(fill="x", padx=40, pady=20)
        
        self.create_button("Create New Level +", 
                          lambda: controller.switch_frame(LevelCreationFrame), 
                          "success", width=20).pack(in_=footer, side="left")
        
        self.play_btn = self.create_button("Play Selected", self.play_selected, 
                                          "primary", width=20)
        self.play_btn.pack(in_=footer, side="right")
        self.play_btn.config(state="disabled", bg="#7f8c8d")
        
        self.selected_world = None
        self.refresh_list()

    def refresh_list(self):
        self.scroll_frame.clear()
        worlds = self.session.get_world_list()
        
        if not worlds:
            tk.Label(self.scroll_frame.inner_frame, text="No saved worlds found.", 
                     fg=self.TEXT_MUTED, bg=self.BG_MEDIUM, font=("Arial", 12)).pack(pady=20)
            return

        for name, info in worlds:
            item = WorldListItem(
                self.scroll_frame.inner_frame, 
                name, info, 
                self.on_select, 
                self.on_delete
            )
            item.pack(fill="x", pady=1)

    def on_select(self, world_name):
        self.selected_world = world_name
        # Update visual selection state
        for widget in self.scroll_frame.inner_frame.winfo_children():
            if isinstance(widget, WorldListItem):
                widget.set_selected(widget.world_name == world_name)
        
        self.play_btn.config(state="normal", bg=self.ACCENT_BLUE)

    def on_delete(self, world_name):
        if messagebox.askyesno("Delete World", f"Are you sure you want to delete '{world_name}'?"):
            self.session.delete_world(world_name)
            if self.selected_world == world_name:
                self.selected_world = None
                self.play_btn.config(state="disabled", bg="#7f8c8d")
            self.refresh_list()

    def play_selected(self):
        if self.selected_world:
            if self.session.load_world(self.selected_world):
                self.controller.switch_frame(GameBoardFrame)
            else:
                messagebox.showerror("Error", "Failed to load world.")


class LevelCreationFrame(BaseFrame):
    """Screen 4: Level Options / Creation."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        # Main container with scrolling for many agents
        main_scroll = ScrollableFrame(self)
        main_scroll.pack(fill="both", expand=True)
        content = main_scroll.inner_frame
        content.configure(bg=self.BG_DARK, padx=40, pady=20)
        
        # Header
        self.create_title_label("Create New World").pack(in_=content, anchor="w", pady=(0, 20))
        
        # --- World Settings ---
        settings_frame = tk.LabelFrame(content, text="World Settings", bg=self.BG_DARK, fg=self.ACCENT_YELLOW, font=("Arial", 12, "bold"))
        settings_frame.pack(fill="x", pady=10, ipady=10)
        
        # Name
        tk.Label(settings_frame, text="World Name:", bg=self.BG_DARK, fg="white").grid(row=0, column=0, padx=10, pady=5, sticky="e")
        self.name_ent = self.create_entry(width=30, parent=settings_frame)
        self.name_ent.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        
        # Difficulty
        tk.Label(settings_frame, text="Difficulty:", bg=self.BG_DARK, fg="white").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.diff_var = tk.StringVar(value="Easy")
        tk.OptionMenu(settings_frame, self.diff_var, "Easy", "Medium", "Hard").grid(row=1, column=1, padx=10, pady=5, sticky="w")
        
        # Size
        tk.Label(settings_frame, text="Grid Size:", bg=self.BG_DARK, fg="white").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        size_frame = tk.Frame(settings_frame, bg=self.BG_DARK)
        size_frame.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        
        self.w_var = tk.IntVar(value=30)
        self.h_var = tk.IntVar(value=30)
        self.link_size = tk.BooleanVar(value=True)
        
        tk.Entry(size_frame, textvariable=self.w_var, width=5).pack(side="left")
        tk.Label(size_frame, text="x", bg=self.BG_DARK, fg="white").pack(side="left", padx=5)
        self.h_ent = tk.Entry(size_frame, textvariable=self.h_var, width=5, state="disabled")
        self.h_ent.pack(side="left")
        
        tk.Checkbutton(size_frame, text="Link W/H", variable=self.link_size, 
                       command=self.toggle_size_link, bg=self.BG_DARK, fg="white", selectcolor=self.BG_DARK).pack(side="left", padx=10)
        
        self.w_var.trace_add("write", self.sync_size)

        # --- Simulation Mode ---
        sim_frame = tk.LabelFrame(content, text="Simulation Mode", bg=self.BG_DARK, fg=self.ACCENT_YELLOW, font=("Arial", 12, "bold"))
        sim_frame.pack(fill="x", pady=20, ipady=10)
        
        self.multi_agent_var = tk.BooleanVar(value=False)
        tk.Checkbutton(sim_frame, text="Enable Multi-Agent Auto-Run", variable=self.multi_agent_var, 
                       command=self.toggle_sim_mode, bg=self.BG_DARK, fg="white", font=("Arial", 11, "bold"), selectcolor=self.BG_DARK).pack(anchor="w", padx=10, pady=5)
        
        # Single Player Options
        self.single_frame = tk.Frame(sim_frame, bg=self.BG_DARK)
        self.single_frame.pack(fill="x", padx=20, pady=5)
        
        tk.Label(self.single_frame, text="Player Vision:", bg=self.BG_DARK, fg="white").pack(side="left")
        self.sp_vis = tk.StringVar(value="Cautious")
        tk.OptionMenu(self.single_frame, self.sp_vis, "Cautious", "Keen-Eyed", "Far-Sight", "Eagle-Eye").pack(side="left", padx=10)
        
        tk.Label(self.single_frame, text="Player Brain:", bg=self.BG_DARK, fg="white").pack(side="left")
        self.sp_brain = tk.StringVar(value="Explorer")
        tk.OptionMenu(self.single_frame, self.sp_brain, "Explorer", "Survivalist", "Smart").pack(side="left", padx=10)
        
        # Multi Agent Options
        self.multi_frame = tk.Frame(sim_frame, bg=self.BG_DARK)
        self.agents_container = tk.Frame(self.multi_frame, bg=self.BG_DARK)
        self.agents_container.pack(fill="x", pady=5)
        
        self.agent_rows = []
        self.add_agent_btn = self.create_button("Add Character +", self.add_agent_row, "secondary", width=15, parent=self.multi_frame)
        self.add_agent_btn.pack(anchor="w", pady=5)
        
        # Footer Buttons
        btn_frame = tk.Frame(content, bg=self.BG_DARK)
        btn_frame.pack(fill="x", pady=30)
        
        self.create_button("Cancel", lambda: controller.switch_frame(LevelSelectionFrame), "danger", parent=btn_frame).pack(side="left")
        self.create_button("Create & Play", self.create_world, "success", parent=btn_frame).pack(side="right")
        
        self.toggle_sim_mode() # Init state

    def toggle_size_link(self):
        if self.link_size.get():
            self.h_ent.config(state="disabled")
            self.h_var.set(self.w_var.get())
        else:
            self.h_ent.config(state="normal")

    def sync_size(self, *args):
        if self.link_size.get():
            try:
                self.h_var.set(self.w_var.get())
            except: pass

    def toggle_sim_mode(self):
        if self.multi_agent_var.get():
            self.single_frame.pack_forget()
            self.multi_frame.pack(fill="x", padx=20, pady=5)
            if not self.agent_rows:
                self.add_agent_row() # Add at least one
        else:
            self.multi_frame.pack_forget()
            self.single_frame.pack(fill="x", padx=20, pady=5)

    def add_agent_row(self):
        row = AgentConfigRow(self.agents_container, len(self.agent_rows) + 1, self.remove_agent_row)
        row.pack(fill="x", pady=2)
        self.agent_rows.append(row)

    def remove_agent_row(self, row):
        if len(self.agent_rows) > 1:
            row.destroy()
            self.agent_rows.remove(row)
            # Renumber
            for i, r in enumerate(self.agent_rows):
                r.agent_num = i + 1
                r.children[list(r.children.keys())[0]].config(text=f"Agent {i+1}:")

    def create_world(self):
        name = self.name_ent.get().strip()
        if not name:
            messagebox.showerror("Error", "World name required.")
            return
            
        try:
            w, h = self.w_var.get(), self.h_var.get()
            if w < 10 or h < 10: raise ValueError
        except:
            messagebox.showerror("Error", "Invalid dimensions (min 10x10).")
            return

        is_multi = self.multi_agent_var.get()
        players = []
        
        if is_multi:
            for row in self.agent_rows:
                players.append(row.get_config())
        else:
            players.append({
                "name": "Player 1",
                "vision": self.sp_vis.get(),
                "brain": self.sp_brain.get(),
                "color": "#2ecc71"
            })
            
        success = self.session.create_world(
            name, self.diff_var.get(), w, h, players, is_multi
        )
        
        if success:
            self.session.load_world(name)
            self.controller.switch_frame(GameBoardFrame)
        else:
            messagebox.showerror("Error", "World name already exists.")


class GameBoardFrame(BaseFrame):
    """Screen 5: The Game Board."""
    
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        
        self.cell_size = 30
        self.offset_x = 0
        self.offset_y = 0
        self.auto_run_id = None
        self.is_auto_running = False
        
        # Layout
        self.grid_columnconfigure(0, weight=1) # Canvas
        self.grid_columnconfigure(1, weight=0) # Sidebar
        self.grid_rowconfigure(0, weight=1)
        
        # Canvas
        self.canvas = tk.Canvas(self, bg="#ecf0f1")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas.bind("<Configure>", self.on_resize)
        self.canvas.bind("<Motion>", self.on_mouse_hover)
        self.canvas.bind("<Button-1>", self.on_click)
        
        # Sidebar
        self.sidebar = tk.Frame(self, bg=self.BG_MEDIUM, width=300)
        self.sidebar.grid(row=0, column=1, sticky="ns")
        self.sidebar.pack_propagate(False)
        
        self.setup_sidebar()
        self.draw_map()
        self.update_ui()

    def setup_sidebar(self):
        pad = 10
        
        # Title / Info
        tk.Label(self.sidebar, text=self.session.current_world_name, 
                 font=("Helvetica", 14, "bold"), fg=self.ACCENT_YELLOW, bg=self.BG_MEDIUM).pack(pady=(20, 5))
        
        info = f"Level {self.session.config['difficulty']} | {self.session.config['w']}x{self.session.config['h']}"
        tk.Label(self.sidebar, text=info, fg=self.TEXT_MUTED, bg=self.BG_MEDIUM).pack(pady=(0, 10))
        
        # Tile Inspection
        tk.Label(self.sidebar, text="TILE INSPECTION", font=("Arial", 10, "bold"), fg=self.ACCENT_BLUE, bg=self.BG_MEDIUM).pack(pady=(10, 5))
        self.tile_lbl = tk.Label(self.sidebar, text="--", font=("Arial", 12, "bold"), fg="white", bg=self.BG_MEDIUM)
        self.tile_lbl.pack()
        
        self.tile_stats = {}
        for k in ["Strength", "Water", "Food"]:
            self.tile_stats[k] = StatusBar(self.sidebar, k, "#95a5a6", max_value=5)
            self.tile_stats[k].pack(fill="x", padx=pad, pady=2)
            
        tk.Frame(self.sidebar, height=2, bg="#7f8c8d").pack(fill="x", pady=15, padx=pad)
        
        # Agent Stats
        tk.Label(self.sidebar, text="AGENT STATUS", font=("Arial", 10, "bold"), fg=self.ACCENT_BLUE, bg=self.BG_MEDIUM).pack(pady=(5, 5))
        self.agent_name_lbl = tk.Label(self.sidebar, text="Select Agent", font=("Arial", 11), fg="white", bg=self.BG_MEDIUM)
        self.agent_name_lbl.pack()
        
        self.agent_bars = {
            "Strength": StatusBar(self.sidebar, "Strength", "#e74c3c"),
            "Water": StatusBar(self.sidebar, "Water", "#3498db"),
            "Food": StatusBar(self.sidebar, "Food", "#2ecc71"),
            "Gold": StatusBar(self.sidebar, "Gold", "#f1c40f", max_value=100)
        }
        for bar in self.agent_bars.values():
            bar.pack(fill="x", padx=pad, pady=2)
            
        tk.Frame(self.sidebar, height=2, bg="#7f8c8d").pack(fill="x", pady=15, padx=pad)
        
        # Controls
        self.btn_next = self.create_button("Next Turn", self.next_turn, "primary", width=25, parent=self.sidebar)
        self.btn_next.pack(pady=5)
        
        self.btn_auto = self.create_button("Start Auto-Run", self.toggle_auto_run, "warning", width=25, parent=self.sidebar)
        self.btn_auto.pack(pady=5)
        
        self.create_button("Reset Level", self.reset_level, "danger", width=25, parent=self.sidebar).pack(pady=5)
        self.create_button("Save & Exit", self.exit_to_menu, "secondary", width=25, parent=self.sidebar).pack(pady=20)
        
        # Log
        tk.Label(self.sidebar, text="EVENT LOG", font=("Arial", 10, "bold"), fg=self.ACCENT_BLUE, bg=self.BG_MEDIUM).pack(pady=(10, 5))
        self.log_box = tk.Text(self.sidebar, height=8, bg=self.BG_DARK, fg="white", font=("Courier", 8), state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=pad, pady=(0, pad))

    def log(self, msg):
        self.log_box.config(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.config(state="disabled")

    def draw_map(self):
        self.canvas.delete("all")
        m = self.session.game_map
        if not m: return
        
        cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
        if cw < 10: return
        
        cell_w = cw / m.width
        cell_h = ch / m.height
        self.cell_size = min(cell_w, cell_h)
        
        self.offset_x = (cw - (m.width * self.cell_size)) / 2
        self.offset_y = (ch - (m.height * self.cell_size)) / 2
        
        # Draw Terrain
        for r in range(m.height):
            for c in range(m.width):
                sq = m.squares[r][c]
                x1 = self.offset_x + c * self.cell_size
                y1 = self.offset_y + r * self.cell_size
                
                self.canvas.create_rectangle(x1, y1, x1+self.cell_size, y1+self.cell_size, 
                                           fill=sq.terrain.color, outline="")
                
                if sq.items:
                    cx, cy = x1 + self.cell_size/2, y1 + self.cell_size/2
                    self.canvas.create_text(cx, cy, text=sq.items[0].symbol, font=("Arial", int(self.cell_size*0.5), "bold"))

        # Draw Players
        for agent in self.session.players:
            if not agent.is_alive: continue
            
            p = agent.player
            px = self.offset_x + p.col * self.cell_size
            py = self.offset_y + p.row * self.cell_size
            pad = self.cell_size * 0.15
            
            # Draw agent circle
            self.canvas.create_oval(px+pad, py+pad, px+self.cell_size-pad, py+self.cell_size-pad,
                                  fill=agent.color, outline="white", width=2)
            
            # Selection indicator
            if self.session.get_selected_player() == agent:
                self.canvas.create_rectangle(px, py, px+self.cell_size, py+self.cell_size, 
                                           outline="white", width=2)

    def update_ui(self):
        agent = self.session.get_selected_player()
        if agent:
            p = agent.player
            self.agent_name_lbl.config(text=f"{agent.name} ({agent.brain_name})", fg=agent.color)
            self.agent_bars["Strength"].update(p.current_strength, p.max_strength)
            self.agent_bars["Water"].update(p.current_water, p.max_water)
            self.agent_bars["Food"].update(p.current_food, p.max_food)
            self.agent_bars["Gold"].update(p.current_gold)
        else:
            self.agent_name_lbl.config(text="No Agent Selected", fg="white")

    def on_resize(self, event):
        self.draw_map()

    def on_mouse_hover(self, event):
        if not self.session.game_map: return
        c = int((event.x - self.offset_x) // self.cell_size)
        r = int((event.y - self.offset_y) // self.cell_size)
        
        sq = self.session.game_map.get_square(r, c)
        if sq:
            t = sq.terrain
            self.tile_lbl.config(text=t.__class__.__name__, fg=t.color)
            self.tile_stats["Strength"].update(t.movement_cost)
            self.tile_stats["Water"].update(t.water_cost)
            self.tile_stats["Food"].update(t.food_cost)

    def on_click(self, event):
        c = int((event.x - self.offset_x) // self.cell_size)
        r = int((event.y - self.offset_y) // self.cell_size)
        
        if self.session.select_player_at_position(r, c):
            self.update_ui()
            self.draw_map() # Redraw selection box

    def next_turn(self):
        res = self.session.run_turn(log_callback=self.log)
        self.draw_map()
        self.update_ui()
        
        # Handle Traders
        if res["traders_encountered"]:
            self.stop_auto_run()
            agent, trader, sq = res["traders_encountered"][0]
            self.show_trader_popup(agent, trader, sq)
            return

        # Handle Game Over / Victory
        if res["game_over"]:
            self.stop_auto_run()
            if res["all_won"]:
                self.show_overlay("VICTORY!", "All agents have reached the goal!", 
                                [("Reset Level", lambda: self.handle_overlay_action("reset"), "primary"), 
                                 ("Main Menu", lambda: self.handle_overlay_action("menu"), "secondary")])
            else:
                self.show_overlay("SIMULATION ENDED", "All agents are dead or finished.", 
                                [("Reset Level", lambda: self.handle_overlay_action("reset"), "primary"), 
                                 ("Main Menu", lambda: self.handle_overlay_action("menu"), "secondary")])

    def handle_overlay_action(self, action):
        """Handle button clicks from overlay messages."""
        # Remove any overlays
        for widget in self.winfo_children():
            if isinstance(widget, OverlayMessage):
                widget.destroy()
        
        if action == "reset":
            self.reset_level()
        elif action == "menu":
            self.exit_to_menu()

    def toggle_auto_run(self):
        if self.is_auto_running:
            self.stop_auto_run()
        else:
            self.is_auto_running = True
            self.btn_auto.config(text="Stop Auto-Run", bg=self.ACCENT_RED)
            self.btn_next.config(state="disabled")
            self.run_loop()

    def stop_auto_run(self):
        self.is_auto_running = False
        if self.auto_run_id:
            self.after_cancel(self.auto_run_id)
            self.auto_run_id = None
        self.btn_auto.config(text="Start Auto-Run", bg=self.ACCENT_YELLOW)
        self.btn_next.config(state="normal")

    def run_loop(self):
        if self.is_auto_running:
            self.next_turn()
            self.auto_run_id = self.after(2500, self.run_loop)

    def reset_level(self):
        self.stop_auto_run()
        self.session.reset_level()
        self.log("Level reset.")
        self.draw_map()
        self.update_ui()
        # Remove any overlay
        for widget in self.winfo_children():
            if isinstance(widget, OverlayMessage):
                widget.destroy()

    def exit_to_menu(self):
        self.stop_auto_run()
        # Remove any overlay first
        for widget in self.winfo_children():
            if isinstance(widget, OverlayMessage):
                widget.destroy()
        self.session.save_world(self.session.current_world_name)
        self.controller.switch_frame(LevelSelectionFrame)

    def show_overlay(self, title, msg, buttons):
        overlay = OverlayMessage(self, title, msg, buttons)
        overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

    def show_trader_popup(self, agent, trader, sq):
        """Show the trader interaction popup."""
        trade_cost = 10
        if "Friendly" in trader.name:
            trade_cost = 7
        elif "Greedy" in trader.name:
            trade_cost = 15
        
        def on_trade(term, accepted):
            if accepted:
                p = agent.player
                if p.current_gold >= trade_cost:
                    p.current_gold -= trade_cost
                    p.current_food = min(p.max_food, p.current_food + 20)
                    p.current_water = min(p.max_water, p.current_water + 20)
                    self.log(f"[{agent.name}] traded with {trader.name}. (-{trade_cost}G, +20F, +20W)")
                    if not trader.is_repeating:
                        sq.items.remove(trader)
                else:
                    self.log(f"[{agent.name}] couldn't afford trade (needs {trade_cost}G).")
            else:
                self.log(f"[{agent.name}] declined to trade.")
            
            term.destroy()
            self.draw_map()
            self.update_ui()
            if self.is_auto_running:
                self.run_loop()

        term = TraderTerminal(self, trader.name, self.session.current_user, 
                             agent, trade_cost, on_trade)
        self.wait_window(term)


# --- Trader Terminal (Improved) ---
class TraderTerminal(tk.Toplevel):
    """Security checkpoint for trader encounters."""
    
    def __init__(self, parent, trader_name, real_user, agent, cost, on_complete):
        super().__init__(parent)
        self.title(f"Trader Encounter - {trader_name}")
        self.geometry("550x450")
        self.configure(bg="#2c3e50")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        self.real_user = real_user
        self.agent = agent
        self.cost = cost
        self.on_complete = on_complete
        self.step = "USERNAME"
        self.attempts = 3
        
        # Header
        tk.Label(self, text="⚠️ SECURITY CHECKPOINT", font=("Helvetica", 18, "bold"), 
                 fg="#e74c3c", bg="#2c3e50").pack(pady=(20, 5))
        tk.Label(self, text=f"Trader: {trader_name}", font=("Arial", 12), 
                 fg="#f1c40f", bg="#2c3e50").pack(pady=(0, 15))
        
        # Log Area
        log_frame = tk.Frame(self, bg="#34495e", padx=10, pady=10)
        log_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, width=55, font=("Courier", 10), 
                               bg="#1a252f", fg="white", state="disabled", wrap="word")
        self.log_text.pack(fill="both", expand=True)
        
        # Input Area
        input_frame = tk.Frame(self, bg="#2c3e50")
        input_frame.pack(fill="x", padx=20, pady=10)
        
        self.entry = tk.Entry(input_frame, font=("Courier", 12), width=40)
        self.entry.pack(side="left", padx=(0, 10))
        self.entry.bind("<Return>", self.process_input)
        self.entry.focus_set()
        
        tk.Button(input_frame, text="Submit", command=self.process_input, 
                  bg="#3498db", fg="white", font=("Arial", 10, "bold")).pack(side="left")
        
        # Trade Buttons (hidden initially)
        self.trade_frame = tk.Frame(self, bg="#2c3e50")
        
        tk.Button(self.trade_frame, text="✓ Accept Trade", command=lambda: self.finish_trade(True),
                  bg="#2ecc71", fg="white", font=("Arial", 12, "bold"), width=15).pack(side="left", padx=10)
        tk.Button(self.trade_frame, text="✗ Decline", command=lambda: self.finish_trade(False),
                  bg="#e74c3c", fg="white", font=("Arial", 12, "bold"), width=15).pack(side="left", padx=10)
        
        # Leave button
        tk.Button(self, text="Leave (Fail Check)", command=lambda: self.finish_trade(False),
                  bg="#7f8c8d", fg="white", font=("Arial", 9)).pack(pady=15)
        
        # Initial message
        self.write("Trader: Hold it! I need to verify your identity.", "#f39c12")
        self.write("Trader: Enter your USERNAME to proceed.", "#f39c12")
        self.write("", None)

    def write(self, msg, color=None):
        self.log_text.config(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def process_input(self, e=None):
        val = self.entry.get().strip()
        if not val:
            return
        self.write(f"> {val}", "#3498db")
        self.entry.delete(0, "end")
        
        if self.step == "USERNAME":
            if val == self.real_user:
                self.write("System: ✓ USERNAME VERIFIED", "#2ecc71")
                self.write("", None)
                self.write("═" * 45, "#7f8c8d")
                self.write(f"Trader: Welcome, {self.real_user}!", "#f39c12")
                self.write("", None)
                self.write("TRADE OFFER:", "#f1c40f")
                self.write(f"  • You receive: +20 Food, +20 Water", "#2ecc71")
                self.write(f"  • Cost: {self.cost} Gold", "#e74c3c")
                self.write(f"  • Your Gold: {self.agent.player.current_gold}", "#f1c40f")
                self.write("", None)
                
                if self.agent.player.current_gold >= self.cost:
                    self.write("Do you accept this trade?", "#ecf0f1")
                else:
                    self.write("⚠️ You don't have enough gold!", "#e74c3c")
                
                # Show trade buttons, hide input
                self.entry.master.pack_forget()
                self.trade_frame.pack(pady=10)
                self.step = "TRADE"
            else:
                self.attempts -= 1
                if self.attempts > 0:
                    self.write(f"System: ✗ USERNAME MISMATCH. {self.attempts} attempts remaining.", "#e74c3c")
                else:
                    self.write("Trader: You're an impostor! Get out!", "#e74c3c")
                    self.after(1500, lambda: self.finish_trade(False))

    def finish_trade(self, accepted):
        self.on_complete(self, accepted)
