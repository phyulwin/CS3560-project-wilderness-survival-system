"""
Login UI Module - Legacy dialog classes for authentication.

This module is kept for backward compatibility but the main authentication
is now handled through the LoginFrame in main_gui.py.
"""

import tkinter as tk
from tkinter import messagebox


class LoginDialog(tk.Toplevel):
    """
    Login dialog window for authenticating a user.
    Legacy implementation - prefer using LoginFrame for in-window login.
    """
    
    def __init__(self, parent, account_manager, on_success_callback):
        """Initialize login UI with username/password fields."""
        super().__init__(parent)
        self.manager = account_manager
        self.callback = on_success_callback
        
        self.title("Login")
        self.geometry("300x200")
        self.configure(bg="#34495e")
        self.resizable(False, False)
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
        tk.Label(self, text="Username:", bg="#34495e", fg="white").pack(pady=5)
        self.user_ent = tk.Entry(self)
        self.user_ent.pack(pady=5)
        self.user_ent.focus_set()
        
        tk.Label(self, text="Password:", bg="#34495e", fg="white").pack(pady=5)
        self.pass_ent = tk.Entry(self, show="*")
        self.pass_ent.pack(pady=5)
        
        # Bind Enter key
        self.pass_ent.bind("<Return>", lambda e: self.attempt_login())
        
        tk.Button(
            self,
            text="Login",
            command=self.attempt_login,
            bg="#2ecc71",
            fg="white"
        ).pack(pady=15)
    
    def attempt_login(self):
        """Attempt login and route success/failure."""
        u = self.user_ent.get().strip()
        p = self.pass_ent.get()
        
        data, msg = self.manager.load_account(u, p)
        if data:
            self.callback(u, data)
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)


class CreateAccountDialog(tk.Toplevel):
    """Dialog window for creating a new account."""
    
    def __init__(self, parent, account_manager, on_success_callback=None):
        """Initialize account creation UI."""
        super().__init__(parent)
        self.manager = account_manager
        self.callback = on_success_callback
        
        self.title("Create Account")
        self.geometry("300x250")
        self.configure(bg="#34495e")
        self.resizable(False, False)
        
        # Center the dialog
        self.transient(parent)
        self.grab_set()
        
        tk.Label(self, text="New Username:", bg="#34495e", fg="white").pack(pady=5)
        self.user_ent = tk.Entry(self)
        self.user_ent.pack(pady=5)
        self.user_ent.focus_set()
        
        tk.Label(self, text="New Password:", bg="#34495e", fg="white").pack(pady=5)
        self.pass_ent = tk.Entry(self, show="*")
        self.pass_ent.pack(pady=5)
        
        tk.Label(self, text="Confirm Password:", bg="#34495e", fg="white").pack(pady=5)
        self.confirm_ent = tk.Entry(self, show="*")
        self.confirm_ent.pack(pady=5)
        
        # Bind Enter key
        self.confirm_ent.bind("<Return>", lambda e: self.attempt_create())
        
        tk.Button(
            self,
            text="Create",
            command=self.attempt_create,
            bg="#3498db",
            fg="white"
        ).pack(pady=15)
    
    def attempt_create(self):
        """Validate input and create the new account."""
        u = self.user_ent.get().strip()
        p = self.pass_ent.get()
        c = self.confirm_ent.get()
        
        if not u or not p:
            messagebox.showerror("Error", "Fields cannot be empty.", parent=self)
            return
        
        if p != c:
            messagebox.showerror("Error", "Passwords do not match.", parent=self)
            return
        
        success, msg = self.manager.create_account(u, p)
        if success:
            messagebox.showinfo("Success", "Account created! You can now login.", parent=self)
            if self.callback:
                self.callback(u)
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)