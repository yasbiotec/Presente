@echo off
title Criador de Jogo - MODO DIAGNOSTICO
echo =================================================================
echo SCRIPT DE DIAGNOSTICO AVANCADO
echo =================================================================
echo Este script tentara instalar o PyInstaller com mais detalhes
echo para descobrirmos a causa do erro.
echo.
pause
echo.

echo --- PASSO 1: Tentando instalar o PyInstaller (Modo Detalhado) ---
echo A saida a seguir pode ser bem longa. Estamos procurando por erros...
echo.
call .\venv\Scripts\python.exe -m pip install --verbose pyinstaller

REM Checa se o comando anterior falhou
if errorlevel 1 (
    echo.
    echo !--- ERRO CRITICO NA INSTALACAO ---!
    echo A instalacao do PyInstaller FALHOU. O erro esta nas linhas acima.
    echo Geralmente eh um problema de rede, firewall, antivirus ou permissao.
    echo Copie todo este texto e envie para analise.
    echo.
    pause
    exit /b
)

echo.
echo --- PASSO 2: Verificando se o PyInstaller foi realmente instalado ---
echo.
call .\venv\Scripts\python.exe -m pip show pyinstaller

REM O pip show retorna erro se o pacote nao for encontrado
if errorlevel 1 (
    echo.
    echo !--- ERRO DE VERIFICACAO ---!
    echo A instalacao parece ter terminado, mas o PyInstaller AINDA NAO FOI ENCONTRADO.
    echo Isso eh muito incomum e aponta para um problema serio no seu ambiente Python.
    echo Copie todo este texto e envie para analise.
    echo.
    pause
    exit /b
)

echo.
echo --- PASSO 3: PyInstaller encontrado! Tentando criar o .exe ---
echo Por favor, aguarde...
echo.
call .\venv\Scripts\python.exe -m pyinstaller --name Maya --windowed --add-data "assets;assets" --add-data "icon.png;." main.py

if errorlevel 1 (
    echo.
    echo !--- ERRO NA CRIACAO DO EXE ---!
    echo O PyInstaller foi encontrado, mas falhou ao criar o executavel.
    echo Verifique as mensagens de erro acima.
    echo.
    pause
    exit /b
)

echo.
echo =================================================================
echo PROCESSO CONCLUIDO COM SUCESSO!
echo =================================================================
echo.
echo O seu jogo executavel esta na pasta 'dist\Maya'.
echo.
pause