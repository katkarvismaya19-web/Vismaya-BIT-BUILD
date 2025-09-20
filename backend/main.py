# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import api # Import the api router

app = FastAPI(title="PaisaBuddy API")

# --- CORS Middleware ---
# This allows your friend's frontend to communicate with your backend
origins = [
    "http://localhost:3000", # The default port for React
    "http://127.0.0.1:3000",
    # Add other origins if needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the authentication router
# All routes from api.py will be available under the /auth prefix
app.include_router(api.router, prefix="/auth", tags=["Authentication"])

@app.get("/", tags=["Root"])
def read_root():
    """A simple root endpoint to confirm the API is running."""
    return {"message": "Welcome to the PaisaBuddy API!"}