import tkinter as tk
from tkinter import messagebox

class LoginDialog(tk.Toplevel):
    def __init__(self, parent, account_manager, on_success_callback):
        super().__init__(parent)
        self.manager = account_manager
        self.callback = on_success_callback
        
        self.title("Login")
        self.geometry("300x200")
        self.configure(bg="#34495e")
        
        tk.Label(self, text="Username:", bg="#34495e", fg="white").pack(pady=5)
        self.user_ent = tk.Entry(self)
        self.user_ent.pack(pady=5)
        
        tk.Label(self, text="Password:", bg="#34495e", fg="white").pack(pady=5)
        self.pass_ent = tk.Entry(self, show="*")
        self.pass_ent.pack(pady=5)
        
        tk.Button(self, text="Login", command=self.attempt_login, bg="#2ecc71").pack(pady=15)

    def attempt_login(self):
        u = self.user_ent.get()
        p = self.pass_ent.get()
        data, msg = self.manager.load_account(u, p)
        if data:
            messagebox.showinfo("Success", f"Welcome back, {u}!")
            self.callback(u, data)
            self.destroy()
        else:
            messagebox.showerror("Error", msg)

class CreateAccountDialog(tk.Toplevel):
    def __init__(self, parent, account_manager):
        super().__init__(parent)
        self.manager = account_manager
        
        self.title("Create Account")
        self.geometry("300x200")
        self.configure(bg="#34495e")
        
        tk.Label(self, text="New Username:", bg="#34495e", fg="white").pack(pady=5)
        self.user_ent = tk.Entry(self)
        self.user_ent.pack(pady=5)
        
        tk.Label(self, text="New Password:", bg="#34495e", fg="white").pack(pady=5)
        self.pass_ent = tk.Entry(self, show="*")
        self.pass_ent.pack(pady=5)
        
        tk.Button(self, text="Create", command=self.attempt_create, bg="#3498db").pack(pady=15)

    def attempt_create(self):
        u = self.user_ent.get()
        p = self.pass_ent.get()
        if not u or not p:
            messagebox.showerror("Error", "Fields cannot be empty.")
            return
            
        success, msg = self.manager.create_account(u, p)
        if success:
            messagebox.showinfo("Success", "Account created! You can now login.")
            self.destroy()
        else:
            messagebox.showerror("Error", msg)