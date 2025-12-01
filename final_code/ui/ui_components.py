"""
UI Components Module - Reusable UI components and screen frames for the WSS application.

This module provides base classes and common widgets for the single-window
scene-based architecture using tkinter Frame swapping.
"""

import tkinter as tk
from tkinter import ttk, font


# =============================================================================
# BASE CLASSES
# =============================================================================

class BaseFrame(tk.Frame):
    """
    Base class for all screen frames in the application.
    
    Provides common functionality for scene management and styling.
    All screens should inherit from this class.
    """
    
    # Common color scheme
    BG_DARK = "#2c3e50"
    BG_MEDIUM = "#34495e"
    BG_LIGHT = "#ecf0f1"
    
    TEXT_LIGHT = "#ffffff"
    TEXT_DARK = "#2c3e50"
    TEXT_MUTED = "#bdc3c7"
    
    ACCENT_GREEN = "#2ecc71"
    ACCENT_BLUE = "#3498db"
    ACCENT_RED = "#e74c3c"
    ACCENT_YELLOW = "#f1c40f"
    ACCENT_PURPLE = "#9b59b6"
    
    def __init__(self, parent, controller, **kwargs):
        """
        Initialize the base frame.
        
        Args:
            parent: Parent widget (typically the main window container)
            controller: Reference to the MainGUI controller for frame switching
            **kwargs: Additional configuration for the frame
        """
        super().__init__(parent, bg=self.BG_DARK, **kwargs)
        self.controller = controller
        self.session = controller.session
    
    def on_show(self):
        """Called when this frame becomes visible. Override in subclasses."""
        pass
    
    def on_hide(self):
        """Called when this frame is about to be hidden. Override in subclasses."""
        pass
    
    def create_title_label(self, text, size=24, parent=None) -> tk.Label:
        """Create a styled title label."""
        return tk.Label(
            parent or self,
            text=text,
            font=("Helvetica", size, "bold"),
            fg=self.ACCENT_YELLOW,
            bg=self.BG_DARK
        )
    
    def create_subtitle_label(self, text, size=12, parent=None) -> tk.Label:
        """Create a styled subtitle label."""
        return tk.Label(
            parent or self,
            text=text,
            font=("Arial", size),
            fg=self.TEXT_MUTED,
            bg=self.BG_DARK
        )
    
    def create_button(self, text, command, style="primary", width=20, parent=None) -> tk.Button:
        """
        Create a styled button.
        
        Args:
            text: Button text
            command: Callback function
            style: Button style (primary, secondary, danger, success)
            width: Button width in characters
            parent: Parent widget (optional)
        """
        colors = {
            "primary": (self.ACCENT_BLUE, self.TEXT_LIGHT),
            "secondary": ("#95a5a6", self.TEXT_LIGHT),
            "danger": (self.ACCENT_RED, self.TEXT_LIGHT),
            "success": (self.ACCENT_GREEN, self.TEXT_LIGHT),
            "warning": (self.ACCENT_YELLOW, self.TEXT_DARK),
        }
        bg, fg = colors.get(style, colors["primary"])
        
        return tk.Button(
            parent or self,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            font=("Arial", 10, "bold"),
            width=width,
            relief=tk.FLAT,
            cursor="hand2"
        )
    
    def create_entry(self, show=None, width=30, parent=None) -> tk.Entry:
        """Create a styled entry field."""
        return tk.Entry(
            parent or self,
            font=("Arial", 11),
            width=width,
            show=show,
            relief=tk.FLAT,
            bg=self.BG_LIGHT,
            fg=self.TEXT_DARK
        )
    
    def create_label(self, text, fg=None, size=10, parent=None) -> tk.Label:
        """Create a styled label."""
        return tk.Label(
            parent or self,
            text=text,
            font=("Arial", size),
            fg=fg or self.TEXT_LIGHT,
            bg=self.BG_DARK
        )


class StyledCard(tk.Frame):
    """A styled card container with rounded appearance effect."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg=BaseFrame.BG_MEDIUM,
            relief=tk.FLAT,
            **kwargs
        )


class StatusBar(tk.Frame):
    """Horizontal bar for displaying stats with fill indicator."""
    
    def __init__(self, parent, label, color, max_value=100, **kwargs):
        super().__init__(parent, bg=BaseFrame.BG_MEDIUM, **kwargs)
        
        self.max_value = max_value
        self.color = color
        
        # Header with label and value
        header = tk.Frame(self, bg=BaseFrame.BG_MEDIUM)
        header.pack(fill=tk.X)
        
        self.label = tk.Label(
            header,
            text=label,
            font=("Arial", 9, "bold"),
            fg=BaseFrame.TEXT_LIGHT,
            bg=BaseFrame.BG_MEDIUM
        )
        self.label.pack(side=tk.LEFT)
        
        self.value_var = tk.StringVar(value="-- / --")
        self.value_label = tk.Label(
            header,
            textvariable=self.value_var,
            font=("Arial", 9),
            fg=BaseFrame.TEXT_MUTED,
            bg=BaseFrame.BG_MEDIUM
        )
        self.value_label.pack(side=tk.RIGHT)
        
        # Progress bar canvas
        self.canvas = tk.Canvas(
            self,
            height=10,
            bg=BaseFrame.BG_DARK,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.X, pady=(2, 0))
    
    def update(self, current, maximum=None):
        """Update the bar with current and maximum values."""
        import math
        
        if maximum is not None:
            self.max_value = maximum
        
        curr_disp = math.ceil(current)
        max_disp = math.ceil(self.max_value)
        self.value_var.set(f"{curr_disp} / {max_disp}")
        
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        if canvas_width < 1:
            canvas_width = 200
        
        if self.max_value > 0:
            pct = max(0, min(1, current / self.max_value))
            fill_width = pct * canvas_width
            self.canvas.create_rectangle(
                0, 0, fill_width, 10,
                fill=self.color,
                width=0
            )


class ScrollableFrame(tk.Frame):
    """A scrollable frame container for lists."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=BaseFrame.BG_MEDIUM, **kwargs)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(
            self,
            bg=BaseFrame.BG_MEDIUM,
            highlightthickness=0
        )
        self.scrollbar = ttk.Scrollbar(
            self,
            orient=tk.VERTICAL,
            command=self.canvas.yview
        )
        
        # Create inner frame for content
        self.inner_frame = tk.Frame(self.canvas, bg=BaseFrame.BG_MEDIUM)
        
        # Configure canvas
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.inner_frame,
            anchor="nw"
        )
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack widgets
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind events
        self.inner_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Enable mouse wheel scrolling (bound to this widget only, not globally)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.inner_frame.bind("<MouseWheel>", self._on_mousewheel)
    
    def _on_frame_configure(self, event):
        """Update scroll region when inner frame changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Adjust inner frame width to canvas width."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        try:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        except tk.TclError:
            pass  # Widget has been destroyed, ignore
    
    def clear(self):
        """Remove all widgets from the inner frame."""
        for widget in self.inner_frame.winfo_children():
            widget.destroy()


class WorldListItem(tk.Frame):
    """A list item representing a saved world."""
    
    def __init__(self, parent, world_name, world_info, on_select, on_delete, **kwargs):
        super().__init__(parent, bg=BaseFrame.BG_DARK, **kwargs)
        
        self.world_name = world_name
        self.on_select = on_select
        self.is_selected = False
        
        # Pad the item
        self.configure(padx=5, pady=5)
        
        # Main content frame
        content = tk.Frame(self, bg=BaseFrame.BG_DARK)
        content.pack(fill=tk.X, expand=True)
        
        # World name
        self.name_label = tk.Label(
            content,
            text=world_name,
            font=("Arial", 12, "bold"),
            fg=BaseFrame.TEXT_LIGHT,
            bg=BaseFrame.BG_DARK,
            cursor="hand2"
        )
        self.name_label.pack(side=tk.LEFT, padx=5)
        
        # World info
        difficulty = world_info.get("difficulty", "Unknown")
        width = world_info.get("width", 0)
        height = world_info.get("height", 0)
        num_players = len(world_info.get("players", []))
        is_multi = world_info.get("is_multi_agent", False)
        
        mode_text = f"{'Multi-Agent' if is_multi else 'Single'}"
        info_text = f"{difficulty} | {width}x{height} | {mode_text} ({num_players} agent{'s' if num_players != 1 else ''})"
        
        self.info_label = tk.Label(
            content,
            text=info_text,
            font=("Arial", 9),
            fg=BaseFrame.TEXT_MUTED,
            bg=BaseFrame.BG_DARK
        )
        self.info_label.pack(side=tk.LEFT, padx=10)
        
        # Delete button
        self.delete_btn = tk.Button(
            content,
            text="🗑",
            font=("Arial", 10),
            fg=BaseFrame.ACCENT_RED,
            bg=BaseFrame.BG_DARK,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: on_delete(world_name)
        )
        self.delete_btn.pack(side=tk.RIGHT, padx=5)
        
        # Bind click events
        self.bind("<Button-1>", self._on_click)
        self.name_label.bind("<Button-1>", self._on_click)
        self.info_label.bind("<Button-1>", self._on_click)
        content.bind("<Button-1>", self._on_click)
    
    def _on_click(self, event):
        """Handle click to select this world."""
        self.on_select(self.world_name)
    
    def set_selected(self, selected: bool):
        """Update visual state for selection."""
        self.is_selected = selected
        bg = BaseFrame.ACCENT_BLUE if selected else BaseFrame.BG_DARK
        
        self.configure(bg=bg)
        for widget in self.winfo_children():
            widget.configure(bg=bg)
            for child in widget.winfo_children():
                if isinstance(child, (tk.Label, tk.Frame)):
                    child.configure(bg=bg)


class AgentConfigRow(tk.Frame):
    """A row for configuring an agent in multi-agent mode."""
    
    VISION_OPTIONS = ["Cautious", "Keen-Eyed", "Far-Sight", "Eagle-Eye"]
    BRAIN_OPTIONS = ["Explorer", "Survivalist", "Smart"]
    
    def __init__(self, parent, agent_num, on_remove=None, **kwargs):
        super().__init__(parent, bg=BaseFrame.BG_DARK, **kwargs)
        
        self.agent_num = agent_num
        
        # Agent number label
        tk.Label(
            self,
            text=f"Agent {agent_num}:",
            font=("Arial", 10, "bold"),
            fg=BaseFrame.TEXT_LIGHT,
            bg=BaseFrame.BG_DARK,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Name entry
        tk.Label(
            self,
            text="Name:",
            font=("Arial", 9),
            fg=BaseFrame.TEXT_MUTED,
            bg=BaseFrame.BG_DARK
        ).pack(side=tk.LEFT)
        
        self.name_entry = tk.Entry(self, width=12, font=("Arial", 9))
        self.name_entry.insert(0, f"Agent {agent_num}")
        self.name_entry.pack(side=tk.LEFT, padx=5)
        
        # Vision dropdown
        tk.Label(
            self,
            text="Vision:",
            font=("Arial", 9),
            fg=BaseFrame.TEXT_MUTED,
            bg=BaseFrame.BG_DARK
        ).pack(side=tk.LEFT)
        
        self.vision_var = tk.StringVar(value=self.VISION_OPTIONS[0])
        self.vision_combo = ttk.Combobox(
            self,
            textvariable=self.vision_var,
            values=self.VISION_OPTIONS,
            state="readonly",
            width=10
        )
        self.vision_combo.pack(side=tk.LEFT, padx=5)
        
        # Brain dropdown
        tk.Label(
            self,
            text="Brain:",
            font=("Arial", 9),
            fg=BaseFrame.TEXT_MUTED,
            bg=BaseFrame.BG_DARK
        ).pack(side=tk.LEFT)
        
        self.brain_var = tk.StringVar(value=self.BRAIN_OPTIONS[0])
        self.brain_combo = ttk.Combobox(
            self,
            textvariable=self.brain_var,
            values=self.BRAIN_OPTIONS,
            state="readonly",
            width=10
        )
        self.brain_combo.pack(side=tk.LEFT, padx=5)
        
        # Remove button (optional)
        if on_remove:
            tk.Button(
                self,
                text="✕",
                font=("Arial", 9),
                fg=BaseFrame.ACCENT_RED,
                bg=BaseFrame.BG_DARK,
                relief=tk.FLAT,
                cursor="hand2",
                command=lambda: on_remove(self)
            ).pack(side=tk.RIGHT, padx=5)
    
    def get_config(self) -> dict:
        """Get the agent configuration as a dictionary."""
        from core.session import PLAYER_COLORS
        
        return {
            "name": self.name_entry.get() or f"Agent {self.agent_num}",
            "vision": self.vision_var.get(),
            "brain": self.brain_var.get(),
            "color": PLAYER_COLORS[(self.agent_num - 1) % len(PLAYER_COLORS)]
        }


class OverlayMessage(tk.Frame):
    """An overlay message for game over/victory notifications."""
    
    def __init__(self, parent, title, message, button_configs, **kwargs):
        """
        Create an overlay message.
        
        Args:
            parent: Parent widget
            title: Title text
            message: Message body
            button_configs: List of (text, command, style) tuples
        """
        super().__init__(parent, bg="#000000", **kwargs)
        
        # Semi-transparent overlay effect (simulated with dark background)
        self.configure(bg=BaseFrame.BG_DARK)
        
        # Center container
        container = tk.Frame(self, bg=BaseFrame.BG_MEDIUM, padx=30, pady=20)
        container.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        tk.Label(
            container,
            text=title,
            font=("Helvetica", 20, "bold"),
            fg=BaseFrame.ACCENT_YELLOW,
            bg=BaseFrame.BG_MEDIUM
        ).pack(pady=(0, 10))
        
        # Message
        tk.Label(
            container,
            text=message,
            font=("Arial", 12),
            fg=BaseFrame.TEXT_LIGHT,
            bg=BaseFrame.BG_MEDIUM,
            wraplength=400,
            justify=tk.CENTER
        ).pack(pady=(0, 20))
        
        # Buttons
        btn_frame = tk.Frame(container, bg=BaseFrame.BG_MEDIUM)
        btn_frame.pack()
        
        for btn_text, btn_cmd, btn_style in button_configs:
            colors = {
                "primary": (BaseFrame.ACCENT_BLUE, BaseFrame.TEXT_LIGHT),
                "success": (BaseFrame.ACCENT_GREEN, BaseFrame.TEXT_LIGHT),
                "danger": (BaseFrame.ACCENT_RED, BaseFrame.TEXT_LIGHT),
            }
            bg, fg = colors.get(btn_style, colors["primary"])
            
            tk.Button(
                btn_frame,
                text=btn_text,
                command=btn_cmd,
                bg=bg,
                fg=fg,
                font=("Arial", 10, "bold"),
                width=15,
                relief=tk.FLAT,
                cursor="hand2"
            ).pack(side=tk.LEFT, padx=5)


# Legacy support for CustomDropdownDialog
class CustomDropdownDialog(tk.Toplevel):
    """
    A modal dialog to select an option from a list.
    Kept for backward compatibility.
    """
    
    def __init__(self, parent, title, prompt, options):
        """Initialize dialog with title, prompt text, and dropdown options."""
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        self.configure(bg=BaseFrame.BG_MEDIUM)
        
        tk.Label(
            self,
            text=prompt,
            font=("Arial", 10),
            fg=BaseFrame.TEXT_LIGHT,
            bg=BaseFrame.BG_MEDIUM
        ).pack(pady=10)
        
        self.combo = ttk.Combobox(self, values=options, state="readonly")
        self.combo.current(0)
        self.combo.pack(pady=5)
        
        tk.Button(
            self,
            text="OK",
            command=self.on_ok,
            width=10,
            bg=BaseFrame.ACCENT_GREEN,
            fg=BaseFrame.TEXT_LIGHT
        ).pack(pady=10)
        
        # Center the window
        self.transient(parent)
        self.grab_set()
        self.wait_window()
    
    def on_ok(self):
        """Confirm selection and close dialog."""
        self.result = self.combo.get()
        self.destroy()