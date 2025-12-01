"""
Authentication Module - Secure user account management with SHA-256 hashing.
"""

import os
import json
import hashlib
import secrets


class AccountManager:
    """Handles JSON-based user storage with secure password hashing."""
    
    def __init__(self):
        os.makedirs("users", exist_ok=True)
    
    def _hash_password(self, password: str, salt: str) -> str:
        """Hash password with salt using SHA-256."""
        return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()
    
    def _get_path(self, username: str) -> str:
        safe = "".join(c for c in username if c.isalnum() or c in ('_', '-'))
        return f"users/{safe}.json"
    
    def create_account(self, username: str, password: str) -> tuple:
        """Create account with hashed password."""
        if not username or not password:
            return False, "Fields cannot be empty."
        if len(username) < 3:
            return False, "Username must be at least 3 characters."
        if len(password) < 4:
            return False, "Password must be at least 4 characters."
        
        path = self._get_path(username)
        if os.path.exists(path):
            return False, "Account already exists."
        
        salt = secrets.token_hex(16)
        data = {
            "username": username,
            "password_hash": self._hash_password(password, salt),
            "salt": salt,
            "worlds": {}
        }
        
        try:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
            return True, "Account created successfully."
        except IOError as e:
            return False, f"Error: {e}"
    
    def load_account(self, username: str, password: str) -> tuple:
        """Load and verify account."""
        if not username or not password:
            return None, "Fields cannot be empty."
        
        path = self._get_path(username)
        if not os.path.exists(path):
            return None, "Account does not exist."
        
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return None, "Account data corrupted."
        
        # Handle legacy plain-text passwords
        if "password" in data and "password_hash" not in data:
            if data["password"] == password:
                salt = secrets.token_hex(16)
                data["password_hash"] = self._hash_password(password, salt)
                data["salt"] = salt
                del data["password"]
                data.setdefault("worlds", {})
                data.pop("level", None)
                data.pop("saved_config", None)
                data.pop("saved_lives", None)
                self.save_progress(username, data)
                return data, "Success"
            return None, "Incorrect password."
        
        # Verify hashed password
        if self._hash_password(password, data.get("salt", "")) != data.get("password_hash", ""):
            return None, "Incorrect password."
        
        data.setdefault("worlds", {})
        return data, "Success"
    
    def save_progress(self, username: str, data: dict) -> bool:
        """Save user data to file."""
        try:
            with open(self._get_path(username), "w") as f:
                json.dump(data, f, indent=4)
            return True
        except IOError:
            return False