# Script de Teste para Validar o Sistema
# Execute este script antes de agendar a tarefa
# 
# Uso: .\testar_sistema.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTE DO SISTEMA" -ForegroundColor Cyan
Write-Host "  Atualizacao Estoque Minimo e Ideal" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$PastaProjeto = "C:\APP\Atualiza_Estoque_Minimo_Ideal"

# Mudar para a pasta do projeto
Set-Location $PastaProjeto

Write-Host "Pasta do projeto: $PastaProjeto" -ForegroundColor White
Write-Host ""

# ============================================================================
# VERIFICACOES
# ============================================================================

Write-Host "VERIFICANDO REQUISITOS..." -ForegroundColor Yellow
Write-Host ""

$Problemas = 0

# 1. Verificar Python
Write-Host "1. Verificando Python..." -NoNewline
try {
    $PythonVersao = & python --version 2>&1
    Write-Host " OK" -ForegroundColor Green
    Write-Host "    Versao: $PythonVersao" -ForegroundColor Gray
} catch {
    Write-Host " ERRO" -ForegroundColor Red
    Write-Host "    Python nao encontrado!" -ForegroundColor Red
    $Problemas++
}

# 2. Verificar pyodbc
Write-Host "2. Verificando pyodbc..." -NoNewline
try {
    $PyodbcCheck = & python -c "import pyodbc; print('OK')" 2>&1
    if ($PyodbcCheck -match "OK") {
        Write-Host " OK" -ForegroundColor Green
    } else {
        Write-Host " ERRO" -ForegroundColor Red
        Write-Host "    Execute: pip install pyodbc" -ForegroundColor Yellow
        $Problemas++
    }
} catch {
    Write-Host " ERRO" -ForegroundColor Red
    Write-Host "    Execute: pip install pyodbc" -ForegroundColor Yellow
    $Problemas++
}

# 3. Verificar arquivo de conexao
Write-Host "3. Verificando ArqID9.TXT..." -NoNewline
if (Test-Path "ArqID9.TXT") {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " ERRO" -ForegroundColor Red
    Write-Host "    Arquivo ArqID9.TXT nao encontrado na pasta!" -ForegroundColor Red
    $Problemas++
}

# 4. Verificar arquivo principal
Write-Host "4. Verificando atualiza_estoque.py..." -NoNewline
if (Test-Path "atualiza_estoque.py") {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " ERRO" -ForegroundColor Red
    Write-Host "    Arquivo atualiza_estoque.py nao encontrado!" -ForegroundColor Red
    $Problemas++
}

Write-Host ""

# ============================================================================
# RESULTADO DAS VERIFICACOES
# ============================================================================

if ($Problemas -gt 0) {
    Write-Host "ENCONTRADOS $Problemas PROBLEMAS!" -ForegroundColor Red
    Write-Host "   Corrija os problemas acima antes de continuar." -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
} else {
    Write-Host "TODOS OS REQUISITOS ATENDIDOS!" -ForegroundColor Green
    Write-Host ""
}

# ============================================================================
# TESTE DE CONEXAO
# ============================================================================

Write-Host "TESTE DE CONEXAO AO BANCO DE DADOS..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path "testeConexaoBd.py") {
    Write-Host "Executando teste de conexao..." -ForegroundColor Cyan
    & python testeConexaoBd.py
    Write-Host ""
    
    $Continuar = Read-Host "A conexao foi bem-sucedida? (S/N)"
    if ($Continuar -ne "S" -and $Continuar -ne "s") {
        Write-Host "Corrija os problemas de conexao antes de continuar" -ForegroundColor Red
        pause
        exit 1
    }
} else {
    Write-Host "Arquivo testeConexaoBd.py nao encontrado" -ForegroundColor Yellow
    Write-Host "   Pulando teste de conexao..." -ForegroundColor Gray
}

Write-Host ""

# ============================================================================
# EXECUCAO DO PROGRAMA
# ============================================================================

Write-Host "EXECUTAR PROGRAMA PRINCIPAL?" -ForegroundColor Yellow
Write-Host ""
Write-Host "   ATENCAO: Isso ira ATUALIZAR o banco de dados!" -ForegroundColor Yellow
Write-Host "   Certifique-se de ter um backup antes de continuar." -ForegroundColor Yellow
Write-Host ""

$Executar = Read-Host "Deseja executar o programa agora? (S/N)"

if ($Executar -eq "S" -or $Executar -eq "s") {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  EXECUTANDO PROGRAMA..." -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    & python atualiza_estoque.py
    
    $CodigoRetorno = $LASTEXITCODE
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    
    if ($CodigoRetorno -eq 0) {
        Write-Host "  EXECUCAO CONCLUIDA COM SUCESSO!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Verifique os resultados:" -ForegroundColor Yellow
        Write-Host "   - Log de sucesso: log_sucesso.txt" -ForegroundColor White
        Write-Host ""
        
        $VerLog = Read-Host "Deseja visualizar o log agora? (S/N)"
        if ($VerLog -eq "S" -or $VerLog -eq "s") {
            Write-Host ""
            if (Test-Path "log_sucesso.txt") {
                Get-Content "log_sucesso.txt" -Tail 50
            }
        }
    } else {
        Write-Host "  EXECUCAO FALHOU!" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Codigo de retorno: $CodigoRetorno" -ForegroundColor Red
        Write-Host "Verifique os erros:" -ForegroundColor Yellow
        Write-Host "   - Log de erro: log_erro.txt" -ForegroundColor White
        Write-Host ""
        
        if (Test-Path "log_erro.txt") {
            Write-Host "ULTIMAS LINHAS DO LOG DE ERRO:" -ForegroundColor Red
            Write-Host ""
            Get-Content "log_erro.txt" -Tail 20
        }
    }
} else {
    Write-Host ""
    Write-Host "Execucao cancelada pelo usuario" -ForegroundColor Cyan
    Write-Host "   Execute manualmente quando estiver pronto:" -ForegroundColor Gray
    Write-Host "   python atualiza_estoque.py" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TESTE CONCLUIDO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Proximos passos:" -ForegroundColor Yellow
Write-Host "   1. Se tudo funcionou, crie o agendamento:" -ForegroundColor White
Write-Host "      .\criar_agendamento.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "   2. Ou configure manualmente no Agendador de Tarefas:" -ForegroundColor White
Write-Host "      Win + R -> taskschd.msc" -ForegroundColor Cyan
Write-Host ""
pause
