# app/schemas.py
from pydantic import BaseModel, EmailStr

# Schema for creating a new user (data from request body)
class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    password: str

# Schema for user login (data from request body)
class UserLogin(BaseModel):
    user_identifier: str
    password: str

# Schema for a generic message response
class MessageResponse(BaseModel):
    message: str