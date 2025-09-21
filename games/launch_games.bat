@echo off
echo ========================================
echo    PAISABUDDY GAME LAUNCHER
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo [INFO] Python is installed!

:: Check and install dependencies
echo [INFO] Checking game dependencies...
pip install pygame numpy matplotlib >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Could not install dependencies automatically
    echo Please run: pip install pygame numpy matplotlib
)

echo.
echo Select a game to play:
echo.
echo 1. Budget Balance Game
echo 2. Investment Garden Game  
echo 3. Fraud Detective Game
echo 4. Game Launcher Hub (Recommended)
echo 5. Exit
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo Launching Budget Balance Game...
    python budget_balance.py
) else if "%choice%"=="2" (
    echo Launching Investment Garden Game...
    python investment_growth.py
) else if "%choice%"=="3" (
    echo Launching Fraud Detective Game...
    python fraud_detection.py
) else if "%choice%"=="4" (
    echo Launching Game Launcher Hub...
    python game_launcher.py
) else if "%choice%"=="5" (
    echo Goodbye! Thanks for playing!
    exit /b 0
) else (
    echo Invalid choice. Please try again.
    timeout /t 2 >nul
    goto :start
)

echo.
echo Game finished! Press any key to continue...
pause >nul