# backend/auth.py
from fastapi import APIRouter, Depends, HTTPException, status, Cookie, Response
import database
import secrets
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import mysql.connector

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str = "demo"  # Simple demo password

class User(BaseModel):
    id: int
    name: str
    username: str
    balance: float

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
    """Simple login endpoint"""
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # For demo purposes, we'll use a simple check
        cursor.execute(
            "SELECT id, name, username, balance FROM Users WHERE username = %s", 
            (credentials.username,)
        )
        
        user = cursor.fetchone()
        if not user:
            # Create a demo user if it doesn't exist
            cursor.execute(
                """INSERT INTO Users (name, username, email, password_hash, balance) 
                   VALUES (%s, %s, %s, 'demo_hash', 100000.00)""",
                (credentials.username.title(), credentials.username, f"{credentials.username}@demo.com")
            )
            conn.commit()
            user_id = cursor.lastrowid
            user = {
                'id': user_id, 
                'name': credentials.username.title(), 
                'username': credentials.username, 
                'balance': 100000.00
            }
        
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

@router.get("/demo-login/{username}")
def demo_login(username: str, response: Response):
    """Quick demo login for testing"""
    conn = database.get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Check if user exists
        cursor.execute("SELECT id, name, username, balance FROM Users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            # Create demo user
            cursor.execute(
                """INSERT INTO Users (name, username, email, password_hash, balance) 
                   VALUES (%s, %s, %s, 'demo_hash', 100000.00)""",
                (username.title(), username, f"{username}@demo.com")
            )
            conn.commit()
            user_id = cursor.lastrowid
            user = {'id': user_id, 'name': username.title(), 'username': username, 'balance': 100000.00}
        
        # Create session
        session_token = create_session(user['id'])
        
        # Set cookie
        response.set_cookie(
            key="session_token",
            value=session_token,
            max_age=86400,
            httponly=True,
            secure=False,
        )
        
        return {
            "message": f"Demo login successful for {user['name']}!",
            "user": user
        }
        
    finally:
        cursor.close()
        conn.close()