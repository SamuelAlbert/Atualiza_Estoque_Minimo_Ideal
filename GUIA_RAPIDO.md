# ⚡ GUIA RÁPIDO DE USO

## 🚀 Instalação e Configuração (Primeira Vez)

### Passo 1: Verificar Requisitos
```powershell
# Abra o PowerShell na pasta do projeto
cd C:\APP\Atualiza_Estoque_Minimo_Ideal

# Execute o script de teste
.\testar_sistema.ps1
```

### Passo 2: Instalar Dependências (se necessário)
```powershell
pip install pyodbc
```

### Passo 3: Configurar Arquivo de Conexão
Certifique-se que `ArqID9.TXT` está presente na pasta com as credenciais corretas.

### Passo 4: Testar Execução Manual
```powershell
python atualiza_estoque.py
```

### Passo 5: Criar Agendamento Automático
```powershell
# Execute como Administrador
.\criar_agendamento.ps1
```

---

## 📋 Comandos Úteis

### Executar Manualmente
```powershell
python atualiza_estoque.py
```

### Ver Log de Sucesso
```powershell
Get-Content log_sucesso.txt -Tail 50
```

### Ver Log de Erro
```powershell
Get-Content log_erro.txt -Tail 50
```

### Testar Sistema Completo
```powershell
.\testar_sistema.ps1
```

### Criar/Recriar Agendamento
```powershell
.\criar_agendamento.ps1
```

### Abrir Agendador de Tarefas
```powershell
taskschd.msc
```

---

## 🔧 Configurações Principais

### Alterar Filial (no arquivo `atualiza_estoque.py`)
```python
FILIAL_COD = 22  # Altere para o código da sua filial
```

### Alterar Horário de Execução
1. Abra: `taskschd.msc`
2. Localize a tarefa: `Atualizar_Estoque_Minimo_Ideal_ShopControl9`
3. Clique com botão direito → Propriedades
4. Aba "Disparadores" → Editar
5. Altere o horário

---

## 📊 O Que o Programa Faz

### UPDATE 1: Produtos com Vendas (90 dias)
- Calcula média ponderada de vendas (50% + 30% + 20%)
- Define Estoque Mínimo = média × 45 dias
- Define Estoque Ideal = Estoque Mínimo + 20%

### UPDATE 2: Produtos Novos (< 30 dias)
- Define Estoque Mínimo = 1
- Define Estoque Ideal = 1

### UPDATE 3: Produtos Sem Vendas (> 730 dias)
- Define Estoque Mínimo = 0
- Define Estoque Ideal = 0

---

## 🆘 Solução Rápida de Problemas

### Erro: "ArqID9.TXT não encontrado"
- Verifique se o arquivo está na pasta do programa
- Nome do arquivo deve ser exatamente `ArqID9.TXT`

### Erro: "pyodbc não encontrado"
```powershell
pip install pyodbc
```

### Erro: "ODBC Driver não encontrado"
- Baixe e instale: [ODBC Driver 17 for SQL Server](https://docs.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)

### Tarefa Agendada Não Executa
1. Verifique se a tarefa está habilitada
2. Veja histórico: `taskschd.msc` → Tarefa → Aba Histórico
3. Execute teste manual clicando com botão direito → Executar

### Verificar Status da Última Execução
```powershell
Get-ScheduledTask -TaskName "Atualizar_Estoque_Minimo_Ideal_ShopControl9" | Get-ScheduledTaskInfo
```

---

## 📞 Checklist de Manutenção

### Diariamente
- [ ] Verificar se a tarefa executou (verificar timestamp dos logs)

### Semanalmente  
- [ ] Revisar `log_erro.txt` para erros
- [ ] Verificar quantidade de produtos atualizados em `log_sucesso.txt`

### Mensalmente
- [ ] Arquivar logs antigos
- [ ] Validar alguns produtos no banco de dados

---

## 📁 Estrutura de Arquivos

```
C:\APP\Atualiza_Estoque_Minimo_Ideal\
│
├── ArqID9.TXT                    # Credenciais de conexão (OBRIGATÓRIO)
├── atualiza_estoque.py           # Programa principal
├── testeConexaoBd.py             # Teste de conexão
│
├── criar_agendamento.ps1         # Script para criar agendamento
├── testar_sistema.ps1            # Script de teste completo
│
├── log_sucesso.txt               # Log de execuções bem-sucedidas
├── log_erro.txt                  # Log de erros
│
├── README.md                     # Documentação completa
└── GUIA_RAPIDO.md               # Este arquivo
```

---

## ⏰ Agendamento Atual

- **Horário:** Diariamente às 03:00
- **Tarefa:** `Atualizar_Estoque_Minimo_Ideal_ShopControl9`
- **Usuário:** SYSTEM (privilégios elevados)

---

## 💾 Backup Recomendado

Antes da primeira execução:
```sql
-- Backup da tabela Estoque_Atual
SELECT * 
INTO Estoque_Atual_Backup_20260212
FROM Estoque_Atual
WHERE Ordem_Filial = (SELECT Ordem FROM Filiais WHERE Codigo = 22)
```

---

## 📝 Anotações

_Use este espaço para registrar alterações e observações:_

- Data: __________  
  Alteração: _________________________________________________

- Data: __________  
  Alteração: _________________________________________________

- Data: __________  
  Alteração: _________________________________________________

---

**Documentação completa:** Veja `README.md`  
**Versão:** 1.0 - Fevereiro 2026
