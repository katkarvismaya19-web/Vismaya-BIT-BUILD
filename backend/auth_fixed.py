# backend/auth_fixed.py
from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Response
import database
import secrets
import bcrypt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import mysql.connector

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    name: str
    email: str

class User(BaseModel):
    id: int
    name: str
    username: str
    balance: float

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_session(user_id: int) -> str:
    """Create a new session for a user"""
    session_token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(hours=24)  # 24 hour session
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Deactivate existing sessions
        cursor.execute(
            "UPDATE UserSessions SET is_active = FALSE WHERE user_id = %s", 
            (user_id,)
        )
        
        # Create new session
        cursor.execute(
            """INSERT INTO UserSessions (user_id, session_token, expires_at) 
               VALUES (%s, %s, %s)""",
            (user_id, session_token, expires_at)
        )
        
        conn.commit()
        return session_token
        
    finally:
        cursor.close()
        conn.close()

def get_current_user(session_token: Optional[str] = Cookie(None)) -> Optional[User]:
    """Get current user from session token"""
    if not session_token:
        return None
        
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        cursor.execute(
            """SELECT u.id, u.name, u.username, u.balance 
               FROM Users u 
               JOIN UserSessions s ON u.id = s.user_id 
               WHERE s.session_token = %s 
               AND s.is_active = TRUE 
               AND s.expires_at > NOW()""",
            (session_token,)
        )
        
        user_data = cursor.fetchone()
        if user_data:
            return User(**user_data)
        return None
        
    finally:
        cursor.close()
        conn.close()

@router.post("/login")
def login(credentials: LoginRequest, response: Response):
    """Proper login with password validation"""
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Get user with password hash
        cursor.execute(
            "SELECT id, name, username, email, password_hash, balance FROM Users WHERE username = %s", 
            (credentials.username,)
        )
        
        user = cursor.fetchone()
        if not user:
            raise HTTPException(
                status_code=401, 
                detail="Invalid username or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user['password_hash']):
            raise HTTPException(
                status_code=401, 
                detail="Invalid username or password"
            )
        
        # Create session
        session_token = create_session(user['id'])
        
        # Set cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=86400,  # 24 hours
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
        )
        
        return {
            "message": f"Login successful! Welcome, {user['name']}.",
            "user": {
                "id": user['id'],
                "name": user['name'],
                "username": user['username'],
                "balance": user['balance']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/register")
def register(user_data: RegisterRequest, response: Response):
    """Register a new user"""
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if username already exists
        cursor.execute("SELECT id FROM Users WHERE username = %s", (user_data.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Create user
        cursor.execute(
            """INSERT INTO Users (name, username, email, password_hash, balance) 
               VALUES (%s, %s, %s, %s, 10000.00)""",
            (user_data.name, user_data.username, user_data.email, hashed_password)
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        # Create session
        session_token = create_session(user_id)
        
        # Set cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=86400,
            httponly=True,
            secure=False,
        )
        
        return {
            "message": f"Registration successful! Welcome, {user_data.name}!",
            "user": {
                "id": user_id,
                "name": user_data.name,
                "username": user_data.username,
                "balance": 10000.00
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

@router.post("/logout")
def logout(response: Response, session_token: Optional[str] = Cookie(None)):
    """Logout endpoint"""
    if session_token:
        conn = database.get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "UPDATE UserSessions SET is_active = FALSE WHERE session_token = %s",
                (session_token,)
            )
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    response.delete_cookie("session_token")
    return {"message": "Logout successful"}

@router.get("/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return current_user

@router.post("/reset-password/{username}")
def reset_user_password(username: str, new_password: str = "demo123"):
    """Reset a user's password (for demo/admin purposes)"""
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Hash the new password
        hashed_password = hash_password(new_password)
        
        # Update password
        cursor.execute(
            "UPDATE Users SET password_hash = %s WHERE username = %s",
            (hashed_password, username)
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        conn.commit()
        
        return {
            "message": f"Password reset successful for {username}",
            "new_password": new_password
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()