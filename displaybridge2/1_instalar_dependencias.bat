@echo off
title DisplayBridge - Instalando dependencias
color 0B
cd /d "%~dp0"
echo.
echo  ================================================
echo    DisplayBridge - Instalando dependencias
echo  ================================================
echo.
py --version >nul 2>&1
IF %ERRORLEVEL% EQU 0 (SET PYCMD=py) ELSE (SET PYCMD=python)
echo  Instalando...
%PYCMD% -m pip install pywin32 pystray Pillow
echo.
IF %ERRORLEVEL% EQU 0 (
    echo  Instalacao concluida! Execute 2_iniciar.vbs para usar.
) ELSE (
    echo  [AVISO] Algum pacote pode ter falhado. Tente como Administrador.
)
echo.
pause
