@echo off
REM Check if Python is installed
python --version >nul 2>&1
IF ERRORLEVEL 1 (
    echo Python is not installed. Please install Python before running this script.
    exit /b 1
)

REM Check if virtualenv is installed, install if not
pip show virtualenv >nul 2>&1
IF ERRORLEVEL 1 (
    echo virtualenv is not installed. Installing virtualenv...
    pip install virtualenv
)

REM Create virtual environment if it doesn't exist
IF NOT EXIST "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install requirements
IF EXIST "requirements.txt" (
    echo Installing requirements...
    pip install -r requirements.txt
) ELSE (
    echo requirements.txt not found. Please ensure it exists in the project directory.
    exit /b 1
)

REM Check if python-dotenv is installed, install if not
pip show python-dotenv >nul 2>&1
IF ERRORLEVEL 1 (
    echo python-dotenv is not installed. Installing python-dotenv...
    pip install python-dotenv
)

REM Load environment variables from .env file (if it exists)
IF EXIST ".env" (
    echo Loading environment variables from .env file...
    setlocal enabledelayedexpansion
    for /f "tokens=*" %%i in (.env) do (
        set "line=%%i"
        set "line=!line:#=!"
        if not "!line!"=="" (
            setx !line!
        )
    )
)

REM Run the application
echo Running the application...
python main.py
