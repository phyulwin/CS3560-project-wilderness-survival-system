from core.auth import AccountManager
from core.session import GameSession
from ui.main_gui import MainGUI

if __name__ == "__main__":
    # Initialize Core Systems
    auth = AccountManager()
    session = GameSession(auth)
    
    # Launch GUI
    app = MainGUI(session)
    app.mainloop()