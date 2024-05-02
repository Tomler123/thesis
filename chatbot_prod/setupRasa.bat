@echo off
REM Set up virtual environment specifically for Rasa
if not exist "prod\venv" (
    mkdir prod
    cd prod
    python -m venv venv
) else (
    cd prod
)

REM call venv\Scripts\activate
pip install --upgrade pip
pip install rasa
python -m pip install -r requirements.txt
REM Copy necessary Rasa configuration files
echo Copying Rasa configuration files...
xcopy "..\..\chatbot\config.yml" "config.yml" /y
xcopy "..\..\chatbot\credentials.yml" "credentials.yml" /y
xcopy "..\..\chatbot\domain.yml" "domain.yml" /y
xcopy "..\..\chatbot\endpoints.yml" "endpoints.yml" /y
xcopy "..\..\chatbot\actions\*" "actions\" /s /y
xcopy "..\..\chatbot\data\*" "data\" /s /y
xcopy "..\..\chatbot\tests\*" "tests\" /s /y

REM Train Rasa model if needed
echo Training Rasa model...
rasa train

echo Rasa setup complete.
