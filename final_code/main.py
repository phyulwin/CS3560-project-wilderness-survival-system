from auth import AccountManager
from session import GameSession
from main_gui import MainGUI

if __name__ == "__main__":
    # Initialize Core Systems
    auth = AccountManager()
    session = GameSession(auth)
    
    # Launch GUI
    app = MainGUI(session)
    app.mainloop()