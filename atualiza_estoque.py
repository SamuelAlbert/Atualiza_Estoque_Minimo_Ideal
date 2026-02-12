"""
Sistema de Atualização Automática de Estoque Mínimo e Ideal
Shop Control 9
Executa diariamente às 03:00 via Agendador de Tarefas do Windows
"""

import pyodbc
import xml.etree.ElementTree as ET
from datetime import datetime
import os
import sys

# ============================================================================
# CONFIGURAÇÕES
# ============================================================================
FILIAL_COD = 22  # Código da filial (altere conforme necessário)
BANCO_DADOS = "S9_Real"
ARQ_CONEXAO = "ArqID9.TXT"
LOG_SUCESSO = "log_sucesso.txt"
LOG_ERRO = "log_erro.txt"

# ============================================================================
# FUNÇÕES DE LOG
# ============================================================================

def registrar_log(mensagem, tipo="SUCESSO"):
    """Registra mensagem no arquivo de log apropriado"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha_log = f"[{timestamp}] {mensagem}\n"
    
    arquivo_log = LOG_SUCESSO if tipo == "SUCESSO" else LOG_ERRO
    
    try:
        with open(arquivo_log, "a", encoding="utf-8") as f:
            f.write(linha_log)
        print(mensagem)  # Também imprime no console
    except Exception as e:
        print(f"Erro ao escrever log: {e}")

def registrar_separador(tipo="SUCESSO"):
    """Registra uma linha separadora no log"""
    arquivo_log = LOG_SUCESSO if tipo == "SUCESSO" else LOG_ERRO
    try:
        with open(arquivo_log, "a", encoding="utf-8") as f:
            f.write("-" * 80 + "\n")
    except:
        pass

# ============================================================================
# FUNÇÃO DE CONEXÃO
# ============================================================================

def conectar_banco():
    """Lê credenciais do ArqID9.TXT e conecta ao banco de dados"""
    try:
        # Verifica se arquivo de conexão existe
        if not os.path.exists(ARQ_CONEXAO):
            raise FileNotFoundError(f"Arquivo {ARQ_CONEXAO} não encontrado na pasta do programa")
        
        # Lê o arquivo XML
        with open(ARQ_CONEXAO, "r", encoding="utf-8") as file:
            conteudo = file.read()
        
        raiz = ET.fromstring(conteudo)
        
        # Extrai dados de conexão
        servidor = raiz.find("./CONEXAO/Servidor").text
        usuario = raiz.find("./CONEXAO/Usuario").text
        senha = raiz.find("./CONEXAO/Senha").text
        
        if not servidor or not usuario or not senha:
            raise ValueError("Dados de conexão incompletos no arquivo ArqID9.TXT")
        
        # Monta string de conexão
        if servidor.lower().startswith('localhost'):
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};" \
                      f"SERVER={servidor};" \
                      f"DATABASE={BANCO_DADOS};" \
                      f"UID={usuario};PWD={senha};"
            registrar_log(f"Conectando ao servidor LOCAL: {servidor}")
        else:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};" \
                      f"SERVER=tcp:{servidor};" \
                      f"DATABASE={BANCO_DADOS};" \
                      f"UID={usuario};PWD={senha};"
            registrar_log(f"Conectando ao servidor REMOTO: tcp:{servidor}")
        
        # Tenta conectar
        conn = pyodbc.connect(conn_str, timeout=30)
        registrar_log("✅ Conexão estabelecida com sucesso!")
        return conn
        
    except FileNotFoundError as e:
        registrar_log(f"❌ ERRO: {e}", "ERRO")
        raise
    except ET.ParseError as e:
        registrar_log(f"❌ ERRO ao ler XML do arquivo {ARQ_CONEXAO}: {e}", "ERRO")
        raise
    except pyodbc.Error as e:
        registrar_log(f"❌ ERRO ao conectar ao banco de dados: {e}", "ERRO")
        raise
    except Exception as e:
        registrar_log(f"❌ ERRO inesperado ao conectar: {e}", "ERRO")
        raise

# ============================================================================
# FUNÇÕES DE ATUALIZAÇÃO
# ============================================================================

def executar_update_1(cursor, ordem_filial):
    """
    UPDATE 1: Atualiza Estoque_Minimo e Estoque_Ideal para produtos vendidos
    com média ponderada (últimos 90 dias, cadastrados há +30 dias)
    """
    registrar_log("Iniciando UPDATE 1: Produtos com média ponderada de vendas...")
    
    sql = """
    DECLARE @FilialCod INT = ?
    DECLARE @OrdemFilial INT = ?
    DECLARE @DataFinal DATE = GETDATE()
    DECLARE @Data30Dias DATE = DATEADD(DAY, -30, @DataFinal)
    DECLARE @Data60Dias DATE = DATEADD(DAY, -60, @DataFinal)
    DECLARE @Data90Dias DATE = DATEADD(DAY, -90, @DataFinal)

    ;WITH Calculos AS (
        SELECT
            PS.Ordem AS ProdOrdem,
            EA.Ordem_Filial,
            -- Calculo do Estoque Minimo
            CASE 
                WHEN CEILING(
                    (
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data30Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < DATEADD(DAY, 1, @DataFinal)
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.50
                        ) +
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data60Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < @Data30Dias
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.30
                        ) +
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data90Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < @Data60Dias
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.20
                        )
                    ) * 45
                ) <= 0 THEN 0
                WHEN CEILING(
                    (
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data30Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < DATEADD(DAY, 1, @DataFinal)
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.50
                        ) +
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data60Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < @Data30Dias
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.30
                        ) +
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data90Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < @Data60Dias
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.20
                        )
                    ) * 45
                ) = 0 THEN 1
                ELSE CEILING(
                    (
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data30Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < DATEADD(DAY, 1, @DataFinal)
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.50
                        ) +
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data60Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < @Data30Dias
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.30
                        ) +
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data90Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < @Data60Dias
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.20
                        )
                    ) * 45
                )
            END AS Novo_Estoque_Minimo,
            -- Calculo do Estoque Ideal (Estoque Minimo + 20%)
            CASE 
                WHEN CEILING(
                    (
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data30Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < DATEADD(DAY, 1, @DataFinal)
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.50
                        ) +
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data60Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < @Data30Dias
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.30
                        ) +
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data90Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < @Data60Dias
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.20
                        )
                    ) * 45
                ) <= 0 THEN 0
                ELSE CEILING(
                    (
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data30Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < DATEADD(DAY, 1, @DataFinal)
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.50
                        ) +
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data60Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < @Data30Dias
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.30
                        ) +
                        (
                            (SUM(CASE 
                                WHEN M.Data_Passou_Efetivacao_Estoque >= @Data90Dias 
                                     AND M.Data_Passou_Efetivacao_Estoque < @Data60Dias
                                THEN 
                                    CASE 
                                        WHEN M.Tipo_Operacao IN ('VND', 'VPC', 'VEF') THEN MPS.Quantidade
                                        ELSE MPS.Quantidade * -1 
                                    END
                                ELSE 0 
                            END) / 30.0) * 0.20
                        )
                    ) * 45 * 1.20
                )
            END AS Novo_Estoque_Ideal
        FROM
            Estoque_Atual EA
            INNER JOIN Prod_Serv PS ON PS.Ordem = EA.Ordem_Prod_Serv
            INNER JOIN Movimento_Prod_Serv MPS ON MPS.Ordem_Prod_Serv = PS.Ordem
            INNER JOIN Movimento M ON M.Ordem = MPS.Ordem_Movimento
        WHERE
            EA.Ordem_Filial = @OrdemFilial
            AND M.Ordem_Filial = @OrdemFilial
            AND MPS.Linha_Excluida = 0
            AND PS.Tipo = 'N'
            AND PS.Data_Cadastro < DATEADD(DAY, -30, @DataFinal)
            AND M.Data_Passou_Efetivacao_Estoque >= @Data90Dias
            AND M.Data_Passou_Efetivacao_Estoque < DATEADD(DAY, 1, @DataFinal)
            AND M.Data_Passou_Desefetivacao_Estoque IS NULL
            AND M.Data_Passou_Efetivacao_Estoque IS NOT NULL
            AND M.Tipo_Operacao IN ('VND', 'VPC', 'VEF', 'DEV', 'CVE')
        GROUP BY
            PS.Ordem,
            EA.Ordem_Filial
    )
    UPDATE EA
    SET 
        EA.Estoque_Minimo = CASE 
            WHEN C.Novo_Estoque_Minimo > 0 THEN C.Novo_Estoque_Minimo
            ELSE EA.Estoque_Minimo
        END,
        EA.Estoque_Ideal = CASE 
            WHEN C.Novo_Estoque_Ideal > 0 THEN C.Novo_Estoque_Ideal
            ELSE EA.Estoque_Ideal
        END
    FROM
        Estoque_Atual EA
        INNER JOIN Calculos C ON C.ProdOrdem = EA.Ordem_Prod_Serv AND C.Ordem_Filial = EA.Ordem_Filial
    WHERE
        C.Novo_Estoque_Minimo > 0
    """
    
    try:
        cursor.execute(sql, (FILIAL_COD, ordem_filial))
        linhas_afetadas = cursor.rowcount
        registrar_log(f"✅ UPDATE 1 concluído: {linhas_afetadas} registros atualizados")
        return linhas_afetadas
    except Exception as e:
        registrar_log(f"❌ ERRO no UPDATE 1: {e}", "ERRO")
        raise

def executar_update_2(cursor, ordem_filial):
    """
    UPDATE 2: Define Estoque_Minimo = 1 e Estoque_Ideal = 1 
    para produtos novos (cadastrados há menos de 30 dias)
    """
    registrar_log("Iniciando UPDATE 2: Produtos novos (cadastrados há menos de 30 dias)...")
    
    sql = """
    DECLARE @FilialCod INT = ?
    DECLARE @OrdemFilial INT = ?
    DECLARE @DataAtual DATE = GETDATE()
    DECLARE @DataInicial DATE = DATEADD(DAY, -30, @DataAtual)
    DECLARE @DataFinal DATE = @DataAtual

    UPDATE EA
    SET 
        EA.Estoque_Minimo = 1,
        EA.Estoque_Ideal = 1
    FROM
        Estoque_Atual EA
        INNER JOIN Prod_Serv PS ON PS.Ordem = EA.Ordem_Prod_Serv
        INNER JOIN (
            SELECT DISTINCT MPS.Ordem_Prod_Serv
            FROM Movimento M
            JOIN Movimento_Prod_Serv MPS ON MPS.Ordem_Movimento = M.Ordem
            WHERE
                M.Ordem_Filial = @OrdemFilial
                AND MPS.Linha_Excluida = 0
                AND (
                    (
                    M.Tipo_Operacao IN ('VND', 'VPC', 'VEF', 'FPV')
                    AND M.Data_Passou_Desefetivacao_Estoque IS NULL
                    AND M.Data_Passou_Efetivacao_Estoque IS NOT NULL
                    AND M.Data_Passou_Efetivacao_Estoque >= @DataInicial 
                    AND M.Data_Passou_Efetivacao_Estoque < DATEADD(D, 1, @DataFinal)
                    )
                    OR 
                    (
                    M.Tipo_Operacao IN ('DEV', 'CVE')
                    AND M.Data_Passou_Desefetivacao_Estoque IS NULL
                    AND M.Data_Passou_Efetivacao_Estoque IS NOT NULL
                    AND M.Data_Efetivado_Estoque >= @DataInicial 
                    AND M.Data_Efetivado_Estoque < DATEADD(D, 1, @DataFinal)
                    )
                )
        ) MovProdutos ON MovProdutos.Ordem_Prod_Serv = PS.Ordem
    WHERE
        EA.Ordem_Filial = @OrdemFilial
        AND PS.Data_Cadastro >= DATEADD(DAY, -30, @DataAtual)
        AND PS.Tipo = 'N'
    """
    
    try:
        cursor.execute(sql, (FILIAL_COD, ordem_filial))
        linhas_afetadas = cursor.rowcount
        registrar_log(f"✅ UPDATE 2 concluído: {linhas_afetadas} registros atualizados")
        return linhas_afetadas
    except Exception as e:
        registrar_log(f"❌ ERRO no UPDATE 2: {e}", "ERRO")
        raise

def executar_update_3(cursor, ordem_filial):
    """
    UPDATE 3: Zera Estoque_Minimo e Estoque_Ideal 
    para produtos sem movimentação nos últimos 730 dias
    """
    registrar_log("Iniciando UPDATE 3: Produtos sem movimentação nos últimos 730 dias...")
    
    sql = """
    DECLARE @FilialCod INT = ?
    DECLARE @OrdemFilial INT = ?
    DECLARE @DataAtual DATE = GETDATE()
    DECLARE @DataInicial DATE = DATEADD(DAY, -730, @DataAtual)
    DECLARE @DataFinal DATE = @DataAtual

    UPDATE EA
    SET 
        EA.Estoque_Minimo = 0,
        EA.Estoque_Ideal = 0
    FROM
        Estoque_Atual EA
        INNER JOIN Prod_Serv PS ON PS.Ordem = EA.Ordem_Prod_Serv
    WHERE
        PS.Tipo = 'N'
        AND EA.Ordem_Filial = @OrdemFilial
        AND PS.Data_Cadastro < DATEADD(DAY, -30, @DataAtual)
        AND PS.Ordem NOT IN (
            SELECT DISTINCT MPS.Ordem_Prod_Serv
            FROM Movimento M
            JOIN Movimento_Prod_Serv MPS ON MPS.Ordem_Movimento = M.Ordem
            WHERE
                M.Ordem_Filial = @OrdemFilial
                AND MPS.Linha_Excluida = 0
                AND (
                    (
                    M.Tipo_Operacao IN ('VND', 'VPC', 'VEF', 'FPV')
                    AND M.Data_Passou_Desefetivacao_Estoque IS NULL
                    AND M.Data_Passou_Efetivacao_Estoque IS NOT NULL
                    AND M.Data_Passou_Efetivacao_Estoque >= @DataInicial 
                    AND M.Data_Passou_Efetivacao_Estoque < DATEADD(D, 1, @DataFinal)
                    )
                    OR 
                    (
                    M.Tipo_Operacao IN ('DEV', 'CVE')
                    AND M.Data_Passou_Desefetivacao_Estoque IS NULL
                    AND M.Data_Passou_Efetivacao_Estoque IS NOT NULL
                    AND M.Data_Efetivado_Estoque >= @DataInicial 
                    AND M.Data_Efetivado_Estoque < DATEADD(D, 1, @DataFinal)
                    )
                )
        )
    """
    
    try:
        cursor.execute(sql, (FILIAL_COD, ordem_filial))
        linhas_afetadas = cursor.rowcount
        registrar_log(f"✅ UPDATE 3 concluído: {linhas_afetadas} registros atualizados")
        return linhas_afetadas
    except Exception as e:
        registrar_log(f"❌ ERRO no UPDATE 3: {e}", "ERRO")
        raise

# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """Função principal do programa"""
    registrar_separador("SUCESSO")
    registrar_log("=" * 80)
    registrar_log("INÍCIO DA EXECUÇÃO - Atualização de Estoque Mínimo e Ideal")
    registrar_log(f"Filial: {FILIAL_COD}")
    registrar_log("=" * 80)
    
    conn = None
    cursor = None
    
    try:
        # Conecta ao banco de dados
        conn = conectar_banco()
        cursor = conn.cursor()
        
        # Busca a ordem da filial
        registrar_log(f"Buscando Ordem da Filial {FILIAL_COD}...")
        cursor.execute("SELECT Ordem FROM Filiais WHERE Codigo = ?", (FILIAL_COD,))
        resultado = cursor.fetchone()
        
        if not resultado:
            raise ValueError(f"Filial com código {FILIAL_COD} não encontrada no banco de dados")
        
        ordem_filial = resultado[0]
        registrar_log(f"✅ Ordem da Filial encontrada: {ordem_filial}")
        
        # Executa os 3 UPDATEs em sequência
        total_update1 = executar_update_1(cursor, ordem_filial)
        total_update2 = executar_update_2(cursor, ordem_filial)
        total_update3 = executar_update_3(cursor, ordem_filial)
        
        # Confirma as alterações no banco
        conn.commit()
        registrar_log("✅ COMMIT realizado com sucesso")
        
        # Resumo final
        registrar_log("=" * 80)
        registrar_log("RESUMO DA EXECUÇÃO:")
        registrar_log(f"  - UPDATE 1 (Média ponderada): {total_update1} produtos atualizados")
        registrar_log(f"  - UPDATE 2 (Produtos novos): {total_update2} produtos atualizados")
        registrar_log(f"  - UPDATE 3 (Sem movimentação): {total_update3} produtos atualizados")
        registrar_log(f"  - TOTAL GERAL: {total_update1 + total_update2 + total_update3} produtos atualizados")
        registrar_log("✅ EXECUÇÃO CONCLUÍDA COM SUCESSO!")
        registrar_log("=" * 80)
        registrar_separador("SUCESSO")
        
        return 0  # Código de sucesso
        
    except Exception as e:
        registrar_separador("ERRO")
        registrar_log("=" * 80, "ERRO")
        registrar_log(f"❌ FALHA NA EXECUÇÃO: {str(e)}", "ERRO")
        registrar_log("=" * 80, "ERRO")
        registrar_separador("ERRO")
        
        # Faz rollback em caso de erro
        if conn:
            try:
                conn.rollback()
                registrar_log("ROLLBACK executado - nenhuma alteração foi salva", "ERRO")
            except:
                pass
        
        return 1  # Código de erro
        
    finally:
        # Fecha conexões
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            registrar_log("Conexão com banco de dados encerrada")

# ============================================================================
# PONTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    try:
        codigo_retorno = main()
        sys.exit(codigo_retorno)
    except KeyboardInterrupt:
        registrar_log("\n⚠️ Execução interrompida pelo usuário", "ERRO")
        sys.exit(2)
    except Exception as e:
        registrar_log(f"\n❌ Erro fatal não tratado: {e}", "ERRO")
        sys.exit(3)
