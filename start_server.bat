@echo off
echo Starting PaisaBuddy Trading Simulator Backend...
echo.
echo Make sure MySQL is running and the database is set up!
echo.
cd backend
echo Starting server at http://localhost:8000
echo Press Ctrl+C to stop the server
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause