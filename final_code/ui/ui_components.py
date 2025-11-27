import tkinter as tk

# Dialog window for selecting an option from a dropdown
class CustomDropdownDialog(tk.Toplevel):
    
    # Initialize dialog with title, prompt text, and dropdown options
    def __init__(self, parent, title, prompt, options):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.result = None
        tk.Label(self, text=prompt, font=("Helvetica", 12)).pack(padx=20, pady=10)
        self.selected = tk.StringVar(self); self.selected.set(options[0])
        tk.OptionMenu(self, self.selected, *options).pack(padx=20, pady=5)
        tk.Button(self, text="OK", command=self.on_ok).pack(padx=20, pady=15)
        self.grab_set(); self.wait_window(self)
    
    # Confirm selection and close dialog
    def on_ok(self):
        self.result = self.selected.get()
        self.destroy()