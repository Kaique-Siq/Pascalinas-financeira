@echo off
echo.
echo  Pascalina — Build
echo  ==================
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERRO] Python nao encontrado. Instale em https://python.org
    pause
    exit /b 1
)

where pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo  Instalando PyInstaller...
    pip install pyinstaller
)

echo  Compilando...
echo.

pyinstaller ^
    --onefile ^
    --noconsole ^
    --name "Pascalina" ^
    --add-data "static;static" ^
    server.py

if %errorlevel% neq 0 (
    echo.
    echo  [ERRO] Build falhou. Verifique as mensagens acima.
    pause
    exit /b 1
)

echo.
echo  Build concluido!
echo  O executavel esta em: dist\Pascalina.exe
echo  Copie Pascalina.exe para qualquer pasta e execute diretamente.
echo  O arquivo pascalina.db sera criado na mesma pasta do .exe.
echo.
pause
