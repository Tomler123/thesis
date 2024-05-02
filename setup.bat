@echo off

REM Install TensorFlow and other dependencies (if needed, adjust based on your actual requirements.txt)
pip install --upgrade pip
python -m pip install -r requirements.txt

REM Inform the user that Flask dependencies are installed
echo Flask dependencies installation complete.

REM Start Flask app (modify the command to suit your execution environment on Heroku)
python app.py

REM (Optional) Go into the chatbot production setup directory and setup Rasa
REM This section can be removed if you choose not to deploy Rasa on Heroku

REM Start Rasa server (modify the command to suit your execution environment on Heroku)
REM rasa run --enable-api --cors '*' --debug  # (Example Rasa command)

echo Setup complete. Flask and Rasa are running (if Rasa is included).
