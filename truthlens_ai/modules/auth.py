import os
import hashlib
import secrets
from truthlens_ai.database.db_manager import execute_query, execute_insert, execute_scalar

def hash_password(password: str, salt: str = None) -> tuple[str, str]:
    """Hashes password with PBKDF2-HMAC-SHA256 and secure random salt."""
    if salt is None:
        salt = secrets.token_hex(16)
    key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
    return key.hex(), salt

def register_user(username: str, email: str, password: str) -> tuple[bool, str, int | None]:
    """Registers a new user account with secure hashed credentials."""
    username = username.strip()
    email = email.strip().lower()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long.", None
    if '@' not in email or '.' not in email:
        return False, "Please provide a valid email address.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None
    
    existing = execute_scalar("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
    if existing:
        return False, "A user with this username or email already exists.", None
    
    pwd_hash, salt = hash_password(password)
    user_id = execute_insert(
        "INSERT INTO users (username, email, password_hash, salt) VALUES (?, ?, ?, ?)",
        (username, email, pwd_hash, salt)
    )
    return True, "Account registered successfully.", user_id

def authenticate_user(username_or_email: str, password: str) -> tuple[bool, str, dict | None]:
    """Authenticates user credentials."""
    target = username_or_email.strip()
    user = execute_scalar(
        "SELECT id, username, email, password_hash, salt, created_at FROM users WHERE username = ? OR email = ?",
        (target, target.lower())
    )
    if not user:
        return False, "Invalid username or password.", None
    
    expected_hash, _ = hash_password(password, user['salt'])
    if expected_hash != user['password_hash']:
        return False, "Invalid username or password.", None
    
    return True, "Login successful.", {
        'id': user['id'],
        'username': user['username'],
        'email': user['email']
    }

def get_user_profile(user_id: int) -> dict | None:
    """Retrieves user profile data."""
    return execute_scalar("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,))
