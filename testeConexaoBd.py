import pyodbc
import xml.etree.ElementTree as ET

# Lê os dados do arquivo ArqID9.TXT
try:
    with open("ArqID9.TXT", "r", encoding="utf-8") as file:
        conteudo = file.read()
    raiz = ET.fromstring(conteudo)

    servidor = raiz.find("./CONEXAO/Servidor").text
    usuario = raiz.find("./CONEXAO/Usuario").text
    senha = raiz.find("./CONEXAO/Senha").text
    banco = "S9_Real"

    # Detectar se é localhost - não usar tcp: para conexões locais
    if servidor.lower().startswith('localhost'):
        # Conexão local - sem tcp:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};" \
                   f"SERVER={servidor};" \
                   f"DATABASE={banco};" \
                   f"UID={usuario};PWD={senha};"
        print(f"Conectando LOCAL: {servidor}")
    else:
        # Conexão remota - com tcp:
        conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};" \
                   f"SERVER=tcp:{servidor};" \
                   f"DATABASE={banco};" \
                   f"UID={usuario};PWD={senha};"
        print(f"Conectando REMOTO: tcp:{servidor}")

    print("Tentando conectar ao SQL Server...")
    conn = pyodbc.connect(conn_str, timeout=5)
    print("✅ Conexão bem-sucedida!")
    conn.close()

except pyodbc.InterfaceError as ie:
    print("❌ Erro de interface ODBC:", ie)
except pyodbc.OperationalError as oe:
    print("❌ Erro operacional ao conectar:", oe)
except Exception as e:
    print("❌ Erro geral:", e)
