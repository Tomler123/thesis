@echo off
REM Create a virtual environment
python3.7 -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate

REM Install TensorFlow and other dependencies
pip install --upgrade pip
pip install tensorflow -force
pip install flask matplotlib flask_sqlalchemy pyodbc flask_wtf wtforms flask_mail numpy pandas yfinance -force
pip install scikit-learn email_validator -force

REM Inform the user
echo Virtual environment setup complete.


REM start chatbot enviroment
REM call .\chatbot_prod\setupRasa.bat
REM Start app.py
python app.py
