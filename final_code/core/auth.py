import os
import json

# AccountManager handles JSON-based storage of user accounts.
class AccountManager:
    """
    Handles JSON user storage.
    """
    # Ensure the users directory exists.
    def __init__(self):
        os.makedirs("users", exist_ok=True)

    # Create a new account file for the given username and password.
    def create_account(self, username, password):
        path = f"users/{username}.json"
        if os.path.exists(path): return False, "Account exists."
        with open(path, "w") as f:
            json.dump({"username": username, "password": password, "level": 1}, f, indent=4)
        return True, "Created successfully."

    # Load an account and verify the password, returning account data on success.
    def load_account(self, username, password):
        path = f"users/{username}.json"
        if not os.path.exists(path): return None, "No such account."
        with open(path, "r") as f:
            data = json.load(f)
        if data.get("password") != password: return None, "Wrong password."
        return data, "Success"

    # Save the provided user data back to the user's JSON file.
    def save_progress(self, username, data):
        with open(f"users/{username}.json", "w") as f:
            json.dump(data, f, indent=4)