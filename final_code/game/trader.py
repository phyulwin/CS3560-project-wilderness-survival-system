import tkinter as tk
import random
from game.items import Item

# Dialog for trader identity verification
class TraderChatDialog(tk.Toplevel):
    """
    A pop-up window where the user must TYPE their username and level exactly
    to verify identity.
    """
    # Initialize the dialog UI and verification state
    def __init__(self, parent, player, log_callback, username, level):
        super().__init__(parent)
        self.title("Security Check")
        self.geometry("500x500")
        self.transient(parent)
        self.grab_set()
        
        self.player = player
        self.log_callback = log_callback
        self.username = str(username)
        self.level = str(level)
        
        # State tracking: 0 = Needs Name, 1 = Needs Level, 2 = Unlocked, -1 = Failed
        self.verification_step = 0
        
        # --- UI LAYOUT ---
        tk.Label(self, text="SECURITY CHECKPOINT", 
                 font=("Courier", 14, "bold"), fg="#c0392b").pack(pady=10)
        
        # Chat History
        self.txt_chat = tk.Text(self, height=14, width=55, state=tk.DISABLED, bg="#ecf0f1", wrap=tk.WORD)
        self.txt_chat.pack(pady=5, padx=10)
        
        # Input Frame
        input_frame = tk.Frame(self)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Input:").pack(side=tk.LEFT, padx=5)
        
        self.entry_input = tk.Entry(input_frame, width=30)
        self.entry_input.pack(side=tk.LEFT, padx=5)
        self.entry_input.bind("<Return>", lambda event: self.submit_answer()) # Allow pressing Enter
        
        self.btn_submit = tk.Button(input_frame, text="Submit", command=self.submit_answer, bg="#3498db", fg="white")
        self.btn_submit.pack(side=tk.LEFT, padx=5)
        
        # Action Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)
        
        self.btn_trade = tk.Button(btn_frame, text="💰 Trade", command=self.do_trade, bg="#f1c40f", width=12, state=tk.DISABLED)
        self.btn_trade.pack(side=tk.LEFT, padx=5)
        
        self.btn_bye = tk.Button(btn_frame, text="👋 Leave", command=self.do_bye, bg="#e74c3c", fg="white", width=12)
        self.btn_bye.pack(side=tk.LEFT, padx=5)

        # --- START CONVERSATION ---
        self.add_text("System", "BIOMETRIC SCAN FAILED.", "red")
        self.add_text("Trader", "Hold it! I can't verify your identity.", "#d35400")
        self.add_text("Trader", "Please enter your exact USERNAME to proceed.", "#d35400")

    # Append a colored message to the chat history
    def add_text(self, sender, msg, color="black"):
        self.txt_chat.config(state=tk.NORMAL)
        self.txt_chat.insert(tk.END, f"{sender}: ", ("bold",))
        self.txt_chat.insert(tk.END, f"{msg}\n", ("color",))
        self.txt_chat.tag_config("bold", font=("Helvetica", 9, "bold"))
        self.txt_chat.tag_config("color", foreground=color)
        self.txt_chat.see(tk.END)
        self.txt_chat.config(state=tk.DISABLED)

    # Handle user input and advance verification steps
    def submit_answer(self):
        if self.verification_step < 0 or self.verification_step >= 2:
            return # Verification ended

        user_input = self.entry_input.get().strip()
        if not user_input: return # Ignore empty input

        # Clear input box
        self.entry_input.delete(0, tk.END)
        
        # Show user input in chat
        self.add_text("You", user_input, "#2980b9")

        # --- LOGIC CHAIN ---
        if self.verification_step == 0:
            # CHECK 1: USERNAME
            if user_input == self.username:
                self.add_text("System", "USERNAME MATCH CONFIRMED.", "green")
                self.add_text("Trader", "Okay, name matches. Now, what is your current LEVEL?", "#d35400")
                self.verification_step = 1
            else:
                self.fail_verification("Username mismatch.")

        elif self.verification_step == 1:
            # CHECK 2: LEVEL
            if user_input == self.level:
                self.success_verification()
            else:
                self.fail_verification("Level mismatch.")

    # Grant access and enable trading after successful verification
    def success_verification(self):
        self.verification_step = 2
        self.add_text("System", "IDENTITY VERIFIED. ACCESS GRANTED.", "green")
        self.add_text("Trader", "Alright, you're clear. Let's trade.", "#d35400")
        
        # Unlock Trade
        self.btn_trade.config(state=tk.NORMAL)
        # Disable Input
        self.entry_input.config(state=tk.DISABLED)
        self.btn_submit.config(state=tk.DISABLED)

    # Handle failed verification and lock the UI
    def fail_verification(self, reason):
        self.verification_step = -1
        self.add_text("System", f"ERROR: {reason}", "red")
        self.add_text("Trader", "You're an imposter! Get out of here before I call the guards!", "red")
        
        # Lock everything
        self.entry_input.config(state=tk.DISABLED)
        self.btn_submit.config(state=tk.DISABLED)
        self.btn_trade.config(state=tk.DISABLED)

    # Execute trade if player has enough gold
    def do_trade(self):
        if self.player.current_gold >= 5:
            self.player.current_gold -= 5
            self.player.current_food = min(self.player.max_food, self.player.current_food + 10)
            self.player.current_water = min(self.player.max_water, self.player.current_water + 10)
            
            self.add_text("System", "Trade Successful! (-5G, +10F, +10W)", "green")
            self.log_callback("Traded with merchant.")
            self.btn_trade.config(state=tk.DISABLED, text="Traded") 
        else:
            self.add_text("System", "INSUFFICIENT GOLD (Need 5).", "red")

    # Close dialog when player leaves
    def do_bye(self):
        self.add_text("You", "Leaving...", "#2980b9")
        self.update() 
        self.after(500, self.destroy) 

# Item representing a trader that triggers verification dialog
class Trader(Item):
    """
    Trader item that triggers the strict verification dialog.
    """
    # Initialize Trader item representation
    def __init__(self):
        super().__init__(True, "T")

    # Show the verification dialog when player collects the trader
    def on_collect(self, player, log):
        try:
            # Access main window data
            root_window = log.__self__
            username = root_window.session.current_user
            level = root_window.session.user_data.get("level", 1)
            
            dialog = TraderChatDialog(root_window, player, log, username, level)
            root_window.wait_window(dialog) 
        except AttributeError:
            log("Trader error: Unable to verify identity.")