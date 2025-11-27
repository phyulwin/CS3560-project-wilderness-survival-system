import tkinter as tk
from tkinter import ttk

class CustomDropdownDialog(tk.Toplevel):
    """
    A modal dialog to select an option from a list.
    """
    def __init__(self, parent, title, prompt, options):
        super().__init__(parent)
        self.result = None
        self.title(title)
        self.geometry("300x150")
        self.resizable(False, False)
        
        tk.Label(self, text=prompt, font=("Arial", 10)).pack(pady=10)
        
        self.combo = ttk.Combobox(self, values=options, state="readonly")
        self.combo.current(0)
        self.combo.pack(pady=5)
        
        tk.Button(self, text="OK", command=self.on_ok, width=10, bg="#2ecc71").pack(pady=10)
        
        # Center the window
        self.transient(parent)
        self.grab_set()
        self.wait_window()
        
    def on_ok(self):
        self.result = self.combo.get()
        self.destroy()