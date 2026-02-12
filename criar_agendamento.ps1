# Script PowerShell para Criar Tarefa Agendada
# Execute como Administrador no PowerShell
# 
# Uso: .\criar_agendamento.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CRIACAO DE TAREFA AGENDADA" -ForegroundColor Cyan
Write-Host "  Atualizacao Estoque Minimo e Ideal" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ============================================================================
# CONFIGURACOES - Altere conforme necessario
# ============================================================================

$NomeTarefa = "Atualizar_Estoque_Minimo_Ideal_ShopControl9"
$Descricao = "Atualizacao automatica de estoque minimo e ideal - Shop Control 9"
$PastaProjeto = "C:\APP\Atualiza_Estoque_Minimo_Ideal"
$ArquivoPython = "atualiza_estoque.py"
$HorarioExecucao = "03:00"

# ============================================================================
# VALIDACOES
# ============================================================================

Write-Host "Verificando configuracoes..." -ForegroundColor Yellow

# Verificar se esta rodando como Administrador
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "ERRO: Este script precisa ser executado como Administrador!" -ForegroundColor Red
    Write-Host "   Clique com botao direito no PowerShell e selecione 'Executar como Administrador'" -ForegroundColor Yellow
    pause
    exit 1
}

# Verificar se a pasta existe
if (-not (Test-Path $PastaProjeto)) {
    Write-Host "ERRO: Pasta nao encontrada: $PastaProjeto" -ForegroundColor Red
    pause
    exit 1
}

# Verificar se o arquivo Python existe
$CaminhoCompleto = Join-Path $PastaProjeto $ArquivoPython
if (-not (Test-Path $CaminhoCompleto)) {
    Write-Host "ERRO: Arquivo nao encontrado: $CaminhoCompleto" -ForegroundColor Red
    pause
    exit 1
}

# Encontrar caminho do Python
try {
    $PythonPath = (Get-Command python -ErrorAction Stop).Source
    Write-Host "Python encontrado: $PythonPath" -ForegroundColor Green
} catch {
    Write-Host "ERRO: Python nao encontrado no PATH do sistema" -ForegroundColor Red
    Write-Host "   Instale o Python e certifique-se de adicionar ao PATH" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host ""

# ============================================================================
# CRIAR TAREFA AGENDADA
# ============================================================================

Write-Host "Criando tarefa agendada..." -ForegroundColor Yellow

try {
    # Verificar se tarefa ja existe
    $TarefaExistente = Get-ScheduledTask -TaskName $NomeTarefa -ErrorAction SilentlyContinue
    if ($TarefaExistente) {
        Write-Host "Tarefa '$NomeTarefa' ja existe!" -ForegroundColor Yellow
        $Resposta = Read-Host "   Deseja substituir? (S/N)"
        if ($Resposta -ne "S" -and $Resposta -ne "s") {
            Write-Host "Operacao cancelada pelo usuario" -ForegroundColor Red
            pause
            exit 0
        }
        Unregister-ScheduledTask -TaskName $NomeTarefa -Confirm:$false
        Write-Host "   Tarefa antiga removida" -ForegroundColor Yellow
    }

    # Criar acao (executar Python)
    $Acao = New-ScheduledTaskAction `
        -Execute $PythonPath `
        -Argument $ArquivoPython `
        -WorkingDirectory $PastaProjeto

    # Criar gatilho (diariamente as 03:00)
    $Gatilho = New-ScheduledTaskTrigger `
        -Daily `
        -At $HorarioExecucao

    # Configuracoes adicionais
    $Configuracoes = New-ScheduledTaskSettingsSet `
        -StartWhenAvailable `
        -RestartCount 3 `
        -RestartInterval (New-TimeSpan -Minutes 5) `
        -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries

    # Criar e registrar a tarefa
    Register-ScheduledTask `
        -TaskName $NomeTarefa `
        -Description $Descricao `
        -Action $Acao `
        -Trigger $Gatilho `
        -Settings $Configuracoes `
        -RunLevel Highest `
        -User "SYSTEM" `
        -Force | Out-Null

    Write-Host ""
    Write-Host "TAREFA CRIADA COM SUCESSO!" -ForegroundColor Green
    Write-Host ""
    Write-Host "DETALHES DA TAREFA:" -ForegroundColor Cyan
    Write-Host "   Nome: $NomeTarefa" -ForegroundColor White
    Write-Host "   Horario: Diariamente as $HorarioExecucao" -ForegroundColor White
    Write-Host "   Pasta: $PastaProjeto" -ForegroundColor White
    Write-Host "   Script: $ArquivoPython" -ForegroundColor White
    Write-Host ""

    # Perguntar se deseja executar teste
    Write-Host "Deseja executar um teste agora? (S/N)" -ForegroundColor Yellow
    $RespostaTeste = Read-Host

    if ($RespostaTeste -eq "S" -or $RespostaTeste -eq "s") {
        Write-Host ""
        Write-Host "Executando teste..." -ForegroundColor Yellow
        Start-ScheduledTask -TaskName $NomeTarefa
        Start-Sleep -Seconds 2
        
        # Verificar status
        $Status = (Get-ScheduledTask -TaskName $NomeTarefa).State
        Write-Host "   Status da tarefa: $Status" -ForegroundColor White
        Write-Host ""
        Write-Host "   Aguarde alguns segundos e verifique os arquivos de log:" -ForegroundColor Cyan
        Write-Host "   - $PastaProjeto\log_sucesso.txt" -ForegroundColor White
        Write-Host "   - $PastaProjeto\log_erro.txt" -ForegroundColor White
    }

} catch {
    Write-Host ""
    Write-Host "ERRO ao criar tarefa agendada:" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    pause
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  CONCLUIDO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para gerenciar a tarefa:" -ForegroundColor Yellow
Write-Host "   1. Pressione Win + R" -ForegroundColor White
Write-Host "   2. Digite: taskschd.msc" -ForegroundColor White
Write-Host "   3. Localize: $NomeTarefa" -ForegroundColor White
Write-Host ""
pause
