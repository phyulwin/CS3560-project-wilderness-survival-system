"""
Wilderness Survival System (WSS) – Application Entry Point
----------------------------------------------------------

This module initializes the core subsystems for the Wilderness Survival System
game environment. It provisions authentication, establishes a user session,
and deploys the primary graphical interface.

Execution begins here when the application is launched by the end user.
"""

from core.auth import AccountManager
from core.session import GameSession
from ui.main_gui import WildernessSurvivalApp

if __name__ == "__main__":
    # Initialize Core Systems
    auth = AccountManager()
    session = GameSession(auth)
    
    # Launch GUI
    app = WildernessSurvivalApp(session)
    app.mainloop()