import tkinter as tk
from tkinter import messagebox

# Login dialog window for authenticating a user
class LoginDialog(tk.Toplevel):

    # Initialize login UI with username/password fields
    def __init__(self, parent, auth_manager, on_success):
        super().__init__(parent)
        self.title("Login")
        self.auth = auth_manager
        self.on_success = on_success
        self.geometry("300x160")
        
        tk.Label(self, text="Username").pack(pady=5)
        self.u_entry = tk.Entry(self); self.u_entry.pack()
        tk.Label(self, text="Password").pack(pady=5)
        self.p_entry = tk.Entry(self, show="*"); self.p_entry.pack()
        
        # Login Button Only
        tk.Button(self, text="Login", command=self.do_login, width=15, bg="#2ecc71").pack(pady=15)

    # Attempt login and route success/failure
    def do_login(self):
        u = self.u_entry.get(); p = self.p_entry.get()
        data, msg = self.auth.load_account(u, p)
        if data:
            self.destroy()
            self.on_success(u, data)
        else:
            messagebox.showerror("Error", msg)

# Dialog window for creating a new account
class CreateAccountDialog(tk.Toplevel):

    # Initialize account creation UI
    def __init__(self, parent, auth_manager):
        super().__init__(parent)
        self.title("Create Account")
        self.auth = auth_manager
        self.geometry("300x160")
        
        tk.Label(self, text="New Username").pack(pady=5)
        self.u_entry = tk.Entry(self); self.u_entry.pack()
        tk.Label(self, text="New Password").pack(pady=5)
        self.p_entry = tk.Entry(self, show="*"); self.p_entry.pack()
        
        # Create Button Only
        tk.Button(self, text="Create Account", command=self.do_create, width=15, bg="#3498db").pack(pady=15)
    
    # Validate input and create the new account
    def do_create(self):
        u = self.u_entry.get(); p = self.p_entry.get()
        if not u or not p:
            messagebox.showerror("Error", "Please enter username and password.")
            return

        ok, msg = self.auth.create_account(u, p)
        if ok:
            messagebox.showinfo("Success", msg + "\nYou can now Login.")
            self.destroy()
        else:
            messagebox.showerror("Error", msg)