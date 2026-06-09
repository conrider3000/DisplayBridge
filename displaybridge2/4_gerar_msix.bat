@echo off
title DisplayBridge - Gerando MSIX
color 0A
cd /d "%~dp0"
echo.
echo  ================================================
echo    DisplayBridge - Gerando pacote MSIX
echo  ================================================
echo.

IF NOT EXIST "dist\DisplayBridge\DisplayBridge.exe" (
    echo  [ERRO] Compile o exe primeiro com 3_gerar_instalador.bat
    pause & exit /b 1
)
echo  [1/3] DisplayBridge.exe encontrado!

SET "MAKEAPPX="
IF EXIST "C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe" (
    SET "MAKEAPPX=C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64\makeappx.exe"
    GOTO found
)
FOR /D %%G IN ("C:\Program Files (x86)\Windows Kits\10\bin\10*") DO (
    IF EXIST "%%G\x64\makeappx.exe" SET "MAKEAPPX=%%G\x64\makeappx.exe"
)
FOR /D %%G IN ("C:\Program Files\Windows Kits\10\bin\10*") DO (
    IF EXIST "%%G\x64\makeappx.exe" SET "MAKEAPPX=%%G\x64\makeappx.exe"
)
:found

IF "%MAKEAPPX%"=="" (
    echo  [ERRO] Windows SDK nao encontrado!
    pause & exit /b 1
)
echo  [2/3] Windows SDK encontrado!

echo  [3/3] Montando MSIX...
IF EXIST "msix_package" rmdir /s /q msix_package
mkdir msix_package\Assets
xcopy "dist\DisplayBridge\*" "msix_package\" /E /I /Q
copy "AppxManifest.xml" "msix_package\" >nul
copy "Assets\*" "msix_package\Assets\" >nul
IF NOT EXIST "msix" mkdir msix
"%MAKEAPPX%" pack /d msix_package /p msix\DisplayBridge_1.0.1.0.msix /nv

IF %ERRORLEVEL% EQU 0 (
    echo.
    echo  ================================================
    echo    Sucesso! msix\DisplayBridge_1.0.1.0.msix
    echo  ================================================
) ELSE (
    echo  [ERRO] Falha ao gerar MSIX!
)
echo.
pause
