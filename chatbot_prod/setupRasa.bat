@echo off

REM Get the current directory
set "currentFolder=%CD%"

REM Empty the current folder apart from the setupscript
for %%F in ("%currentFolder%\*") do (
    if /I not "%%~nxF"=="setupRasa.bat" del /Q "%%F"
)

REM create prodcution file
mkdir prod
REM go into prodcutin folder
cd prod


REM Create a virtual environment
python3.7 -m venv venv

REM Activate the virtual environment
call venv\Scripts\activate

REM Install TensorFlow and other dependencies
pip install --upgrade pip
pip install rasa

REM Inform the user
echo Virtual environment setup complete.

REM Start rasa
rasa init --no-prompt

    REM Array of source file paths
   set sourceFiles1="..\..\chatbot\config.yml" "..\..\chatbot\credentials.yml" "..\..\chatbot\domain.yml" "..\..\chatbot\endpoints.yml"
for %%F in (%sourceFiles1%) do (
    xcopy "%%F" ".\%%~nxF" /y
)


    set sourceFiles2="..\..\chatbot\actions\__init__.py" "..\..\chatbot\actions\actions.py"
for %%F in (%sourceFiles2%) do (
    xcopy "%%F" ".\actions\%%~nxF" /y
)

    set source3="..\..\chatbot\data\nlu.yml" "..\..\chatbot\data\stories.yml" "..\..\chatbot\data\rules.yml"
for %%F in (%source3%) do (
    xcopy "%%F" ".\data\%%~nxF" /y
)

   set source4="..\..\chatbot\tests\test_stories.yml"
for %%F in (%source4%) do (
    xcopy "%%F" ".\tests\%%~nxF" /y
)

    REM Loop through each source file and copy it to the current folder preserving directory structure
   
rasa train
echo Files copied successfully.
