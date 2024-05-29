@echo off


REM Function to check Python version
:CHECK_PYTHON_VERSION
for /f "delims=" %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
for /f "tokens=2 delims= " %%v in ("%PYTHON_VERSION%") do set PYTHON_VERSION=%%v

for /f "delims=" %%v in ('python3.7 --version 2^>^&1') do set PYTHON3_7_VERSION=%%v
for /f "tokens=2 delims= " %%v in ("%PYTHON3_7_VERSION%") do set PYTHON3_7_VERSION=%%v

IF "%PYTHON_VERSION%"=="3.7.9" (
    set CREATE_VENV_CMD=python -m venv venv
) ELSE IF "%PYTHON3_7_VERSION%"=="3.7.9" (
    set CREATE_VENV_CMD=python3.7 -m venv venv
) ELSE (
    echo Python 3.7.9 is not installed. Please install Python 3.7.9 before running this script.
    exit /b 1
)

REM Check if ODBC Driver 17 for SQL Server is installed
REM Using REG query to check if the driver is installed
reg query "HKLM\SOFTWARE\ODBC\ODBCINST.INI\ODBC Drivers" /v "ODBC Driver 17 for SQL Server" >nul 2>&1
IF ERRORLEVEL 1 (
    echo ODBC Driver 17 for SQL Server is not installed.
    echo Please download and install it from:
    echo https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
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
    %CREATE_VENV_CMD%
    IF ERRORLEVEL 1 (
        echo Failed to create virtual environment. Please ensure Python is correctly installed.
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Install requirements
IF EXIST "requirements.txt" (
    echo Installing requirements...
    pip install -r requirements.txt
    IF ERRORLEVEL 1 (
        echo Failed to install requirements. Please check your requirements.txt file.
        exit /b 1
    )
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
python app.py
