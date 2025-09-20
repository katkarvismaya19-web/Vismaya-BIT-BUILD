# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import api # Import the api router
import trade
import auth

app = FastAPI(title="PaisaBuddy API")

# --- CORS Middleware ---
# This allows your frontend to communicate with your backend
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5501",
    "http://127.0.0.1:5501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include the authentication router
# All routes from api.py will be available under the /auth prefix

app.include_router(api.router, prefix="/auth", tags=["Authentication"])
app.include_router(auth.router, prefix="/api/auth", tags=["Session Auth"])
app.include_router(trade.router, prefix="/api/trade", tags=["Trading"])

@app.get("/", tags=["Root"])
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the PaisaBuddy API!"}