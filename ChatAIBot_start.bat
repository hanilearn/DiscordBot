@echo off
echo Starting the bot...

REM 檢查 Python 版本並決定使用 python 或 python3
set PYTHON_CMD=python
python --version 2>nul
if errorlevel 1 (
    echo Python not found with 'python' command, trying 'python3'...
    set PYTHON_CMD=python3
    python3 --version 2>nul
    if errorlevel 1 (
        echo No Python 3.x installation found. Please install Python 3.
        pause
        exit /b 1
    )
)

REM 檢查版本是否為 3.x
for /f "tokens=2 delims= " %%v in ('%PYTHON_CMD% --version') do (
    set VERSION=%%v
)
echo Detected Python version: %VERSION%
echo %VERSION%| findstr /b "3." >nul
if errorlevel 1 (
    echo This script requires Python 3.x, but found %VERSION%.
    pause
    exit /b 1
)

REM 檢查 venv 資料夾是否存在
if not exist "venv" (
    echo Virtual environment not found. Creating one...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Please check your Python installation.
        pause
        exit /b 1
    )
)

REM 啟動虛擬環境
call venv\Scripts\activate
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

REM 檢查 requirements.txt 是否存在，並檢查是否已安裝套件
if exist "requirements.txt" (
    REM 檢查 pip 是否有安裝過套件（使用標記檔案判斷）
    if not exist "venv\installed.flag" (
        echo Installing dependencies from requirements.txt...
        pip install -r requirements.txt
        if errorlevel 1 (
            echo Failed to install dependencies.
            pause
            exit /b 1
        )
        REM 安裝成功後建立標記檔案
        echo Installed > venv\installed.flag
    ) else (
        echo Dependencies already installed.
    )
) else (
    echo requirements.txt not found. Skipping dependency installation.
)

REM 執行 Python 程式
echo Starting ChatAIBot.py...
%PYTHON_CMD% ChatAIBot.py
if errorlevel 1 (
    echo Failed to start ChatAIBot.py.
    pause
    exit /b 1
)

pause