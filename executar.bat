@echo off
REM ============================================================================
REM Script Batch para Executar Atualização de Estoque
REM Sistema: Shop Control 9
REM ============================================================================

echo ========================================
echo   Atualizacao de Estoque Minimo e Ideal
echo   Shop Control 9
echo ========================================
echo.

REM Mudar para a pasta do script
cd /d "%~dp0"

echo Pasta atual: %CD%
echo.

REM Verificar se Python está disponível
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Instale o Python e adicione ao PATH do sistema.
    pause
    exit /b 1
)

REM Verificar se arquivo principal existe
if not exist "atualiza_estoque.py" (
    echo ERRO: Arquivo atualiza_estoque.py nao encontrado!
    pause
    exit /b 1
)

REM Verificar se arquivo de conexão existe
if not exist "ArqID9.TXT" (
    echo ERRO: Arquivo ArqID9.TXT nao encontrado!
    pause
    exit /b 1
)

echo Executando atualizacao de estoque...
echo.

REM Executar o programa Python
python atualiza_estoque.py

REM Capturar código de retorno
set CODIGO_RETORNO=%errorlevel%

echo.
echo ========================================

if %CODIGO_RETORNO% equ 0 (
    echo   EXECUCAO CONCLUIDA COM SUCESSO!
    echo ========================================
    echo.
    echo Verifique o log: log_sucesso.txt
) else (
    echo   EXECUCAO FALHOU!
    echo ========================================
    echo.
    echo Codigo de retorno: %CODIGO_RETORNO%
    echo Verifique o log: log_erro.txt
)

echo.
REM Descomentar a linha abaixo para manter a janela aberta após execução
REM pause

exit /b %CODIGO_RETORNO%
