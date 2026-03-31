@echo off
cd /d "%~dp0"

echo ========================================
echo   Transcription de document - Lancement
echo ========================================
echo.

:: Vérifie Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installe.
    echo Telecharge et installe Python sur https://www.python.org/downloads/
    echo Coche bien "Add Python to PATH" pendant l'installation.
    echo.
    pause
    exit /b
)

:: Vérifie Tesseract
tesseract --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Tesseract n'est pas installe.
    echo Telecharge et installe Tesseract sur :
    echo https://github.com/UB-Mannheim/tesseract/wiki
    echo Puis relance ce fichier.
    echo.
    pause
    exit /b
)

:: Crée l'environnement virtuel si absent
if not exist ".venv" (
    echo Creation de l'environnement virtuel...
    python -m venv .venv
)

:: Active l'environnement
call .venv\Scripts\activate.bat

:: Installe les dépendances si besoin
echo Installation des dependances (quelques minutes)...
pip install --upgrade pip
pip install -r requirements.txt


echo Lancement de l'application...

python app.py

echo Ouvre ton navigateur sur : http://localhost:7860

pause