@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

if "%SARVAM_API_KEY%"=="" (
    if exist .env (
        for /f "usebackq tokens=1,2 delims==" %%a in (".env") do (
            if "%%a"=="SARVAM_API_KEY" set SARVAM_API_KEY=%%b
        )
    )
)

if "%SARVAM_API_KEY%"=="" (
    echo Error: SARVAM_API_KEY is not set and not found in .env
    exit /b 1
)

echo [1/4] Generating Sarvam AI voiceover and timing.json...
python make_voice.py
if errorlevel 1 exit /b 1

echo [2/4] Rendering QC stills sheet...
python horror.py qc
if errorlevel 1 exit /b 1

echo [3/4] Rendering full video and SFX...
python horror.py full
if errorlevel 1 exit /b 1

echo [4/4] Mixing final audio and video...
python horror.py mix
if errorlevel 1 exit /b 1

echo === Pipeline Completed! Output: final.mp4 ===
