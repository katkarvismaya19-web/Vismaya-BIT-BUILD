# app/api.py
from fastapi import APIRouter, Depends, HTTPException, status
from mysql.connector.errors import IntegrityError

import database, schemas, crud, security

# Create a new router object
router = APIRouter()

@router.post("/register", response_model=schemas.MessageResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_data: schemas.UserCreate, db = Depends(database.get_db_connection)):
    """API endpoint to register a new user."""
    try:
        crud.create_user(db=db, user=user_data)
        return {"message": "Registration successful!"}
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists."
        )
    finally:
        db.close()

@router.post("/login")
def login_user(credentials: schemas.UserLogin, db = Depends(database.get_db_connection)):
    """API endpoint for a user to log in."""
    user_record = crud.get_user_by_identifier(db=db, identifier=credentials.user_identifier)
    db.close()

    if not user_record or not security.verify_password(credentials.password, user_record['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please try again.",
        )
    
    return {
        "message": f"Login successful! Welcome, {user_record['name']}.",
        "user": { "id": user_record['id'], "name": user_record['name'] }
    }