@echo off
title DisplayBridge - Gerando .exe + Instalador
color 0A
cd /d "%~dp0"
echo.
echo  ================================================
echo    DisplayBridge v2 - Gerando .exe + Instalador
echo  ================================================
echo.

py --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (SET PYCMD=py) ELSE (SET PYCMD=python)
echo  [1/4] Python encontrado!

echo  [2/4] Instalando PyInstaller...
%PYCMD% -m pip install pyinstaller --quiet
echo         PyInstaller OK!

echo  [3/4] Compilando DisplayBridge.exe...
%PYCMD% -m PyInstaller --noconfirm displaybridge.spec
IF %ERRORLEVEL% NEQ 0 (echo [ERRO] Falha ao compilar! & pause & exit /b 1)
echo         DisplayBridge.exe gerado em dist\

echo  [4/4] Gerando instalador...
SET INNO="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
IF NOT EXIST %INNO% SET INNO="C:\Program Files\Inno Setup 6\ISCC.exe"
IF NOT EXIST %INNO% (
    echo  [AVISO] Inno Setup nao encontrado. Instale em: https://jrsoftware.org/isdl.php
    pause & exit /b 0
)
IF NOT EXIST "instalador" mkdir instalador
%INNO% installer.iss
IF %ERRORLEVEL% EQU 0 (
    echo.
    echo  ================================================
    echo    Sucesso! Instalador: instalador\DisplayBridge_Setup_v2.0.0.exe
    echo  ================================================
) ELSE (
    echo  [ERRO] Falha ao gerar instalador!
)
echo.
pause
