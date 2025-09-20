# app/crud.py
import mysql.connector
import schemas, security

def create_user(db: mysql.connector.connection.MySQLConnection, user: schemas.UserCreate):
    """Inserts a new user record into the database."""
    hashed_pass = security.hash_password(user.password)
    cursor = db.cursor()
    
    sql = "INSERT INTO Users (name, username, email, password_hash) VALUES (%s, %s, %s, %s)"
    val = (user.name, user.username, user.email, hashed_pass)
    
    try:
        cursor.execute(sql, val)
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        raise err  # Re-raise the exception to be handled by the API endpoint
    finally:
        cursor.close()

def get_user_by_identifier(db: mysql.connector.connection.MySQLConnection, identifier: str):
    """Fetches a user by their username or email."""
    cursor = db.cursor(dictionary=True) # dictionary=True is very useful
    
    sql = "SELECT id, name, password_hash FROM Users WHERE username = %s OR email = %s"
    cursor.execute(sql, (identifier, identifier))
    user_record = cursor.fetchone()
    
    cursor.close()
    return user_record