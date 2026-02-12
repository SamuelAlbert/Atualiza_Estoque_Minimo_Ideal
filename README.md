# Sistema de Atualização Automática de Estoque Mínimo e Ideal
## Shop Control 9

---

## 📋 Descrição do Sistema

Este sistema automatiza a atualização diária dos campos `Estoque_Minimo` e `Estoque_Ideal` no banco de dados do Shop Control 9, baseando-se em análise de vendas históricas e comportamento de produtos.

### Funcionalidades

O programa executa **3 atualizações sequenciais**:

1. **UPDATE 1 - Produtos com Histórico de Vendas (Média Ponderada)**
   - **Critério:** Produtos cadastrados há mais de 30 dias com vendas nos últimos 90 dias
   - **Cálculo:** Média ponderada das vendas (50% últimos 30 dias, 30% de 31-60 dias, 20% de 61-90 dias)
   - **Estoque Mínimo:** Média ponderada × 45 dias (arredondado para cima, mínimo 1)
   - **Estoque Ideal:** Estoque Mínimo + 20% (arredondado para cima)
   - **Regra:** Não atualiza se o cálculo resultar em valor zero ou negativo

2. **UPDATE 2 - Produtos Novos**
   - **Critério:** Produtos cadastrados há menos de 30 dias
   - **Ação:** Define `Estoque_Minimo = 1` e `Estoque_Ideal = 1`

3. **UPDATE 3 - Produtos Sem Movimentação**
   - **Critério:** Produtos sem vendas nos últimos 730 dias (2 anos)
   - **Ação:** Define `Estoque_Minimo = 0` e `Estoque_Ideal = 0`

---

## 📁 Estrutura de Arquivos

```
c:\APP\Atualiza_Estoque_Minimo_Ideal\
│
├── ArqID9.TXT                  # Arquivo XML com credenciais de conexão (OBRIGATÓRIO)
├── atualiza_estoque.py         # Programa principal
├── log_sucesso.txt             # Log de execuções bem-sucedidas
├── log_erro.txt                # Log de erros e falhas
└── README.md                   # Este arquivo de documentação
```

---

## ⚙️ Configuração

### 1. Arquivo de Conexão (ArqID9.TXT)

O arquivo `ArqID9.TXT` deve estar na mesma pasta do programa e conter as credenciais de conexão no formato XML:

```xml
<SHOP9>
<CONEXAO>
<Tipo></Tipo>
<Servidor>localhost\shopcontrol9</Servidor>
<Usuario>sa</Usuario>
<Senha>SuaSenhaAqui</Senha>
<Timeout>60</Timeout>
<Descricao>Normal</Descricao>
</CONEXAO>
</SHOP9>
```

### 2. Parâmetros Configuráveis

Abra o arquivo `atualiza_estoque.py` e ajuste os parâmetros no início do arquivo:

```python
# ============================================================================
# CONFIGURAÇÕES
# ============================================================================
FILIAL_COD = 22  # Código da filial (altere conforme necessário)
BANCO_DADOS = "S9_Real"
ARQ_CONEXAO = "ArqID9.TXT"
LOG_SUCESSO = "log_sucesso.txt"
LOG_ERRO = "log_erro.txt"
```

- **FILIAL_COD:** Código da filial a ser processada (padrão: 22)
- **BANCO_DADOS:** Nome do banco de dados (padrão: "S9_Real")

---

## 🚀 Execução Manual

Para testar o programa manualmente:

1. Abra o **PowerShell** ou **Prompt de Comando**
2. Navegue até a pasta do programa:
   ```powershell
   cd C:\APP\Atualiza_Estoque_Minimo_Ideal
   ```
3. Execute o programa:
   ```powershell
   python atualiza_estoque.py
   ```

### Códigos de Retorno

- **0:** Execução bem-sucedida
- **1:** Erro durante execução (falha de conexão, SQL, etc.)
- **2:** Interrupção pelo usuário (Ctrl+C)
- **3:** Erro fatal não tratado

---

## ⏰ Agendamento Automático (Execução Diária às 03:00)

### Método 1: Agendador de Tarefas do Windows (Recomendado)

#### Passo 1: Abrir o Agendador de Tarefas

1. Pressione `Win + R`
2. Digite `taskschd.msc` e pressione Enter
3. Clique em **"Criar Tarefa..."** no painel direito

#### Passo 2: Configurar Aba "Geral"

- **Nome:** Atualizar Estoque Mínimo e Ideal - Shop Control 9
- **Descrição:** Atualização automática de estoque mínimo e ideal às 03:00
- **Configurar para:** Windows 10 (ou sua versão do Windows)
- **Marcar:** ☑ Executar estando o usuário conectado ou não
- **Marcar:** ☑ Executar com privilégios mais altos
- **Não marcar:** ☐ Oculta (deixe desmarcado para ver logs)

#### Passo 3: Configurar Aba "Disparadores"

1. Clique em **"Novo..."**
2. Configure:
   - **Iniciar a tarefa:** Diariamente
   - **Iniciar:** (Data de hoje)
   - **Recorrente a cada:** 1 dias
   - **Horário:** 03:00:00
   - **Marcar:** ☑ Habilitado
3. Clique em **OK**

#### Passo 4: Configurar Aba "Ações"

1. Clique em **"Novo..."**
2. Configure:
   - **Ação:** Iniciar um programa
   - **Programa/script:** `python` ou `C:\Python\python.exe` (caminho completo do Python)
   - **Adicionar argumentos:** `atualiza_estoque.py`
   - **Iniciar em:** `C:\APP\Atualiza_Estoque_Minimo_Ideal`
3. Clique em **OK**

> **⚠️ IMPORTANTE:** Se você não souber o caminho do Python, abra o PowerShell e digite:
> ```powershell
> where.exe python
> ```
> Copie o caminho completo e cole no campo "Programa/script"

#### Passo 5: Configurar Aba "Condições"

- **Desmarcar:** ☐ Iniciar tarefa apenas se o computador estiver ocioso
- **Desmarcar:** ☐ Parar se o computador deixar de estar ocioso
- **Desmarcar:** ☐ Iniciar a tarefa apenas se o computador estiver conectado à energia CA

#### Passo 6: Configurar Aba "Configurações"

- **Marcar:** ☑ Permitir que a tarefa seja executada sob demanda
- **Marcar:** ☑ Executar a tarefa assim que possível após uma inicialização agendada ser perdida
- **Se a tarefa falhar, reiniciar a cada:** 5 minutos
- **Tentar reiniciar até:** 3 vezes

#### Passo 7: Salvar e Testar

1. Clique em **OK** para salvar a tarefa
2. Digite a senha do usuário do Windows (se solicitado)
3. **Teste manual:**
   - Na lista de tarefas, localize a tarefa criada
   - Clique com botão direito → **Executar**
   - Verifique os arquivos de log gerados

---

### Método 2: Script PowerShell de Agendamento

Você pode usar este script para criar a tarefa automaticamente:

```powershell
# Script para criar tarefa agendada
# Execute como Administrador

$NomeTarefa = "Atualizar_Estoque_Minimo_Ideal"
$Descricao = "Atualização automática de estoque mínimo e ideal - Shop Control 9"
$PastaProjeto = "C:\APP\Atualiza_Estoque_Minimo_Ideal"
$ArquivoPython = "atualiza_estoque.py"
$HorarioExecucao = "03:00"

# Encontrar caminho do Python
$PythonPath = (Get-Command python).Source

# Criar ação
$Acao = New-ScheduledTaskAction -Execute $PythonPath `
    -Argument $ArquivoPython `
    -WorkingDirectory $PastaProjeto

# Criar gatilho (diariamente às 03:00)
$Gatilho = New-ScheduledTaskTrigger -Daily -At $HorarioExecucao

# Configurações adicionais
$Configuracoes = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 5)

# Criar tarefa
Register-ScheduledTask -TaskName $NomeTarefa `
    -Description $Descricao `
    -Action $Acao `
    -Trigger $Gatilho `
    -Settings $Configuracoes `
    -RunLevel Highest `
    -User "SYSTEM"

Write-Host "✅ Tarefa '$NomeTarefa' criada com sucesso!"
Write-Host "📅 Executará diariamente às $HorarioExecucao"
```

**Como usar:**
1. Salve como `criar_agendamento.ps1`
2. Abra PowerShell como **Administrador**
3. Execute: `.\criar_agendamento.ps1`

---

## 📊 Logs do Sistema

### Log de Sucesso (log_sucesso.txt)

Registra todas as execuções bem-sucedidas com:
- Data/hora de execução
- Quantidade de produtos atualizados em cada UPDATE
- Resumo total da execução

**Exemplo:**
```
--------------------------------------------------------------------------------
================================================================================
[2026-02-12 03:00:01] INÍCIO DA EXECUÇÃO - Atualização de Estoque Mínimo e Ideal
[2026-02-12 03:00:01] Filial: 22
================================================================================
[2026-02-12 03:00:01] Conectando ao servidor LOCAL: localhost\shopcontrol9
[2026-02-12 03:00:02] ✅ Conexão estabelecida com sucesso!
[2026-02-12 03:00:02] Buscando Ordem da Filial 22...
[2026-02-12 03:00:02] ✅ Ordem da Filial encontrada: 5
[2026-02-12 03:00:02] Iniciando UPDATE 1: Produtos com média ponderada de vendas...
[2026-02-12 03:00:15] ✅ UPDATE 1 concluído: 243 registros atualizados
[2026-02-12 03:00:15] Iniciando UPDATE 2: Produtos novos (cadastrados há menos de 30 dias)...
[2026-02-12 03:00:17] ✅ UPDATE 2 concluído: 18 registros atualizados
[2026-02-12 03:00:17] Iniciando UPDATE 3: Produtos sem movimentação nos últimos 730 dias...
[2026-02-12 03:00:22] ✅ UPDATE 3 concluído: 87 registros atualizados
[2026-02-12 03:00:22] ✅ COMMIT realizado com sucesso
================================================================================
[2026-02-12 03:00:22] RESUMO DA EXECUÇÃO:
[2026-02-12 03:00:22]   - UPDATE 1 (Média ponderada): 243 produtos atualizados
[2026-02-12 03:00:22]   - UPDATE 2 (Produtos novos): 18 produtos atualizados
[2026-02-12 03:00:22]   - UPDATE 3 (Sem movimentação): 87 produtos atualizados
[2026-02-12 03:00:22]   - TOTAL GERAL: 348 produtos atualizados
[2026-02-12 03:00:22] ✅ EXECUÇÃO CONCLUÍDA COM SUCESSO!
================================================================================
[2026-02-12 03:00:22] Conexão com banco de dados encerrada
--------------------------------------------------------------------------------
```

### Log de Erro (log_erro.txt)

Registra todas as falhas e erros com:
- Data/hora do erro
- Descrição detalhada do problema
- Pilha de erro (quando aplicável)

**Exemplo:**
```
--------------------------------------------------------------------------------
================================================================================
[2026-02-12 03:00:01] ❌ FALHA NA EXECUÇÃO: Arquivo ArqID9.TXT não encontrado na pasta do programa
================================================================================
[2026-02-12 03:00:01] ROLLBACK executado - nenhuma alteração foi salva
--------------------------------------------------------------------------------
```

---

## 🔍 Solução de Problemas

### Erro: "Arquivo ArqID9.TXT não encontrado"

**Causa:** O arquivo de conexão não está na pasta do programa

**Solução:**
- Verifique se `ArqID9.TXT` está em `C:\APP\Atualiza_Estoque_Minimo_Ideal`
- Certifique-se que o nome do arquivo está correto (maiúsculas/minúsculas)

---

### Erro: "pyodbc.Error: ('IM002'..."

**Causa:** Driver ODBC não instalado

**Solução:**
1. Baixe o driver: [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server)
2. Instale o driver
3. Execute o programa novamente

---

### Erro: "Filial com código X não encontrada"

**Causa:** O código da filial não existe no banco de dados

**Solução:**
1. Abra `atualiza_estoque.py`
2. Altere a linha `FILIAL_COD = 22` para o código correto da sua filial
3. Salve e execute novamente

---

### Erro: "Timeout expired" ou "Connection refused"

**Causa:** Banco de dados inacessível ou servidor SQL Server desligado

**Solução:**
- Verifique se o SQL Server está rodando
- Teste a conexão com `testeConexaoBd.py`
- Verifique credenciais em `ArqID9.TXT`
- Verifique configurações de firewall

---

### Tarefa Agendada Não Executa

**Possíveis causas e soluções:**

1. **Python não encontrado:**
   - Use caminho completo do Python na tarefa
   - Encontre com: `where.exe python`

2. **Permissões insuficientes:**
   - Configure a tarefa para "Executar com privilégios mais altos"
   - Use conta SYSTEM ou Administrador

3. **Computador desligado no horário:**
   - Marque "Executar assim que possível após inicialização perdida"

4. **Verifique histórico da tarefa:**
   - Agendador de Tarefas → Biblioteca do Agendador de Tarefas
   - Clique na tarefa → Aba "Histórico"

---

## 📝 Requisitos do Sistema

### Software Necessário

- **Python 3.7 ou superior**
- **pyodbc** (biblioteca Python)
- **ODBC Driver 17 for SQL Server** (ou superior)
- **Windows 7/8/10/11** (para agendamento)

### Instalação de Dependências

```powershell
# Instalar biblioteca pyodbc
pip install pyodbc
```

---

## 🔒 Segurança

### Boas Práticas

1. **Proteja o arquivo ArqID9.TXT:**
   - Configure permissões restritas (somente administradores)
   - Não compartilhe este arquivo
   - Use senhas fortes para o usuário SQL

2. **Monitore os logs:**
   - Verifique regularmente `log_erro.txt`
   - Arquive logs antigos periodicamente

3. **Backup:**
   - Faça backup do banco antes de executar pela primeira vez
   - Mantenha backup da pasta do programa

---

## 📞 Suporte e Manutenção

### Alteração de Filial

Para processar outra filial, edite `atualiza_estoque.py`:

```python
FILIAL_COD = 30  # Altere para o código da filial desejada
```

### Alteração de Horário

No Agendador de Tarefas:
1. Localize a tarefa
2. Clique com botão direito → Propriedades
3. Aba "Disparadores" → Editar
4. Altere o horário
5. OK → OK

### Múltiplas Filiais

Para processar várias filiais, crie uma tarefa agendada para cada filial:
- Duplique a tarefa existente
- Altere o nome (ex: "Atualizar Estoque - Filial 30")
- Edite a ação para usar um arquivo Python específico (ou passe o código da filial como argumento)

---

## 📄 Licença e Créditos

Sistema desenvolvido para automatização de processos no Shop Control 9.

**Desenvolvido em:** Fevereiro de 2026

---

## 📌 Observações Importantes

⚠️ **ATENÇÃO:**
- O programa executa **COMMIT** automático após todos os UPDATEs
- Em caso de erro, executa **ROLLBACK** (nenhuma alteração é salva)
- Sempre teste em ambiente de homologação antes de usar em produção
- A primeira execução pode demorar mais devido ao volume de dados

✅ **Recomendações:**
- Execute manualmente a primeira vez para validar
- Monitore os logs nas primeiras semanas
- Documente qualquer alteração feita no código
- Mantenha backups regulares do banco de dados

---

**Fim da Documentação**
