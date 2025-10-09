# database_manager.py
import mysql.connector
from mysql.connector import errorcode
import sys
import datetime
import threading

# SQL para criação de tabelas (permanece o mesmo)
SQL_CREATE_PROGRAMADO_TABLE_MYSQL = """
CREATE TABLE IF NOT EXISTS programado (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_hora_programado DATETIME NOT NULL,
    remetente_nome VARCHAR(255),
    remetente_telefone VARCHAR(50),
    destinatario_nome VARCHAR(255),
    destinatario_telefone VARCHAR(50)
) ENGINE=InnoDB;
"""
SQL_CREATE_CLIENTES_TABLE_MYSQL = """
CREATE TABLE IF NOT EXISTS clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL UNIQUE,
    telefone VARCHAR(50),
    ncliente VARCHAR(50) UNIQUE NULL
) ENGINE=InnoDB;
"""
SQL_CREATE_ENTRADAS_TABLE_MYSQL = """
CREATE TABLE IF NOT EXISTS entradas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_hora_registro DATETIME NOT NULL,
    codigo VARCHAR(50) NOT NULL UNIQUE,
    remetente_nome VARCHAR(255),
    remetente_telefone VARCHAR(50),
    destinatario_nome VARCHAR(255),
    destinatario_telefone VARCHAR(50),
    modalidade VARCHAR(100),
    atendente_registro VARCHAR(100),
    tipo_pacote VARCHAR(100)
) ENGINE=InnoDB;
"""
SQL_CREATE_SAIDAS_TABLE_MYSQL = """
CREATE TABLE IF NOT EXISTS saidas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_envelope VARCHAR(50) NOT NULL,
    data_hora_registro_original DATETIME,
    remetente_nome VARCHAR(255),
    remetente_telefone VARCHAR(50),
    destinatario_nome VARCHAR(255),
    destinatario_telefone VARCHAR(50),
    modalidade VARCHAR(100),
    atendente_registro_original VARCHAR(100),
    tipo_pacote VARCHAR(100),
    data_hora_saida DATETIME NOT NULL,
    atendente_saida VARCHAR(100)
) ENGINE=InnoDB;
"""

_show_message_thread_safe = None

def _get_show_message_func():
    global _show_message_thread_safe
    if _show_message_thread_safe is None:
        try:
            from ui_manager import show_message_thread_safe
            _show_message_thread_safe = show_message_thread_safe
        except ImportError:
            _show_message_thread_safe = lambda msg_type, title, message: print(f"DB_MSG_ERROR ({msg_type}) {title}: {message}")
    return _show_message_thread_safe


db_conn = None
db_mysql_config = {}

def set_db_config(config):
    global db_mysql_config
    db_mysql_config = config

def get_db_connection():
    global db_conn, db_mysql_config
    show_message = _get_show_message_func()

    if db_conn is None or not db_conn.is_connected():
        try:
            if not db_mysql_config:
                show_message("error", "Erro Config BD", "Configurações do banco de dados MySQL não carregadas.")
                return None
            db_conn = mysql.connector.connect(
                host=db_mysql_config['host'], user=db_mysql_config['user'],
                password=db_mysql_config['password'], database=db_mysql_config['database'],
                port=db_mysql_config.get('port', 3306), connection_timeout=10,
                use_pure=True
            )
        except mysql.connector.Error as err:
            db_conn = None
            error_title = "Erro Conexão MySQL"
            error_message = f"Falha ao conectar ao MySQL: {err}"
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                error_message = f"Usuário ('{db_mysql_config.get('user')}') ou senha do MySQL incorretos."
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                error_message = f"Banco de dados MySQL '{db_mysql_config.get('database')}' não encontrado."
            elif err.errno == errorcode.CR_CONN_HOST_ERROR:
                error_message = f"Não foi possível conectar ao servidor MySQL em '{db_mysql_config.get('host')}:{db_mysql_config.get('port', 3306)}'. Verifique o servidor, a rede e o firewall."
            elif err.errno == errorcode.CR_UNKNOWN_HOST:
                error_message = f"Host MySQL desconhecido: '{db_mysql_config.get('host')}'."
            show_message("error", error_title, error_message)
            print(f"MySQL Connection Error: {err}")
            return None 
        except KeyError as e:
            db_conn = None
            show_message("error", "Erro Config BD", f"Parâmetro de configuração do MySQL ausente no config.ini: {e}")
            return None 
        except Exception as e_gen:
            db_conn = None
            show_message("error", "Erro Desconhecido Conexão DB", f"Erro inesperado ao conectar ao MySQL: {e_gen}")
            return None 
    return db_conn

def init_db(show_message_func):
    global _show_message_thread_safe
    _show_message_thread_safe = show_message_func

    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor()
        
        cursor.execute(SQL_CREATE_CLIENTES_TABLE_MYSQL)
        cursor.execute(SQL_CREATE_ENTRADAS_TABLE_MYSQL)
        cursor.execute(SQL_CREATE_SAIDAS_TABLE_MYSQL)
        cursor.execute(SQL_CREATE_PROGRAMADO_TABLE_MYSQL)
        conn.commit()

        indices = [
            "CREATE INDEX idx_clientes_nome ON clientes (nome)",
            "CREATE INDEX idx_entradas_codigo ON entradas (codigo)",
            "CREATE INDEX idx_programado_rem_tel ON programado (remetente_telefone)",
            "CREATE INDEX idx_programado_dest_tel ON programado (destinatario_telefone)"
        ]

        for sql_command in indices:
            try:
                cursor.execute(sql_command)
            except mysql.connector.Error as err:
                if err.errno != errorcode.ER_DUP_KEYNAME:
                    raise
        
        conn.commit()
        cursor.close()

    except mysql.connector.Error as e:
        _get_show_message_func()("error", "Erro Init DB MySQL", f"Falha ao inicializar/verificar tabelas MySQL: {e}")
        conn.rollback()
        return None
    
    return conn


def processar_envelope_programado(dados_envio, id_programado_para_deletar):
    conn = get_db_connection()
    if not conn: return False
    
    try:
        cursor = conn.cursor()
        
        sql_insert = """
            INSERT INTO entradas (data_hora_registro, codigo, remetente_nome, remetente_telefone,
                                  destinatario_nome, destinatario_telefone, modalidade,
                                  atendente_registro, tipo_pacote)
            VALUES (%(data_hora_registro)s, %(codigo)s, %(remetente_nome)s, %(remetente_telefone)s,
                    %(destinatario_nome)s, %(destinatario_telefone)s, %(modalidade)s,
                    %(atendente_registro)s, %(tipo_pacote)s)
        """
        cursor.execute(sql_insert, dados_envio)
        
        sql_delete = "DELETE FROM programado WHERE id = %s"
        cursor.execute(sql_delete, (id_programado_para_deletar,))
        
        if cursor.rowcount == 0:
            raise Exception(f"A entrada programada (ID: {id_programado_para_deletar}) não foi encontrada para deleção. A operação foi cancelada.")

        conn.commit()
        cursor.close()
        return True

    except Exception as e:
        conn.rollback()
        _get_show_message_func()("error", "Erro de Transação", f"Falha ao processar envelope programado. A operação foi revertida.\n\nErro: {e}")
        return False

def ler_programados_por_remetente(remetente_telefone):
    programados = []
    conn = get_db_connection()
    if not conn: return programados
    try:
        # <<< ALTERAÇÃO AQUI >>>
        # Força o fim da transação atual para obter uma visão atualizada dos dados.
        conn.commit()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT id, destinatario_nome, destinatario_telefone, data_hora_programado
            FROM programado 
            WHERE remetente_telefone = %s 
            ORDER BY data_hora_programado ASC
        """
        cursor.execute(query, (remetente_telefone,))
        programados = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error as e:
        _get_show_message_func()("error", "Erro Leitura Programados", f"Erro ao ler envelopes programados: {e}")
    return programados

def deletar_programado(id_programado):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        query = "DELETE FROM programado WHERE id = %s"
        cursor.execute(query, (id_programado,))
        conn.commit()
        rows_deleted = cursor.rowcount
        cursor.close()
        return rows_deleted > 0
    except mysql.connector.Error as e:
        _get_show_message_func()("error", "Erro ao Deletar Programado", f"Erro ao deletar registro programado: {e}")
        conn.rollback()
        return False

def ler_clientes():
    clientes = {}
    conn = get_db_connection()
    if not conn: return clientes
    try:
        # <<< ALTERAÇÃO AQUI >>>
        conn.commit()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nome, telefone, ncliente FROM clientes ORDER BY nome")
        for row in cursor.fetchall():
            clientes[row['nome']] = {'telefone': row['telefone'], 'ncliente': row['ncliente']}
        cursor.close()
    except mysql.connector.Error as e:
        _get_show_message_func()("error", "Erro Leitura Clientes DB", f"Erro ao ler clientes do MySQL: {e}")
    return clientes

def salvar_cliente(nome_input, telefone_input, ncliente_input=None): 
    show_message = _get_show_message_func()
    nome_limpo = nome_input.strip()
    telefone_limpo = ''.join(filter(str.isdigit, str(telefone_input))).strip()
    ncliente_limpo = ncliente_input.strip() if ncliente_input else None 
    if not nome_limpo:
        show_message("error", "Erro", "Nome do cliente é obrigatório.")
        return False
    if len(nome_limpo.split(' ')) < 2:
        show_message("error", "Erro", "Nome e sobrenome são obrigatórios. Por favor, insira o nome completo.")
        return False
    if not telefone_limpo or not (10 <= len(telefone_limpo) <= 11):
        show_message("error", "Erro", "Telefone inválido. Por favor, insira um número com 10 ou 11 dígitos (DDD + número).")
        return False
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO clientes (nome, telefone, ncliente) 
            VALUES (%s, %s, %s) 
            ON DUPLICATE KEY UPDATE 
                telefone = VALUES(telefone), 
                ncliente = VALUES(ncliente)
        """
        cursor.execute(sql, (nome_limpo, telefone_limpo, ncliente_limpo))
        conn.commit()
        cursor.close()
        show_message("info", "Sucesso", f"Cliente '{nome_limpo}' salvo/atualizado.")
        return True
    except mysql.connector.IntegrityError as e_int:
        show_message("error", "Erro DB", f"Erro de integridade ao salvar cliente '{nome_limpo}'. Nome duplicado ou NCliente já existe? {e_int}")
        conn.rollback()
        return False
    except mysql.connector.Error as e:
        show_message("error", "Erro Salvar Cliente DB", f"Erro ao salvar cliente no MySQL: {e}")
        conn.rollback()
        return False

def salvar_nova_entrada_db(dados_envio):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO entradas (data_hora_registro, codigo, remetente_nome, remetente_telefone,
                                  destinatario_nome, destinatario_telefone, modalidade,
                                  atendente_registro, tipo_pacote)
            VALUES (%(data_hora_registro)s, %(codigo)s, %(remetente_nome)s, %(remetente_telefone)s,
                    %(destinatario_nome)s, %(destinatario_telefone)s, %(modalidade)s,
                    %(atendente_registro)s, %(tipo_pacote)s)
        """
        cursor.execute(sql, dados_envio)
        conn.commit()
        cursor.close()
        return True
    except mysql.connector.IntegrityError as e_int:
        _get_show_message_func()("error", "Erro Código Duplicado", f"Código de envelope '{dados_envio.get('codigo')}' já existe. Tente gerar novamente. {e_int}")
        conn.rollback()
        return False
    except mysql.connector.Error as e:
        _get_show_message_func()("error", "Erro Salvar Entrada DB", f"Erro ao salvar entrada no MySQL: {e}")
        conn.rollback()
        return False

def ler_historico_entradas_db(filter_start_date=None, filter_end_date=None,
                              filter_remetente_nome=None, filter_destinatario_nome=None):
    historico = []
    conn = get_db_connection()
    if not conn: return historico
    query = "SELECT * FROM entradas"
    conditions = []
    params = {}
    if filter_start_date:
        conditions.append("data_hora_registro >= %(start_date)s")
        params['start_date'] = filter_start_date.strftime("%Y-%m-%d %H:%M:%S")
    if filter_end_date:
        end_date_inclusive = filter_end_date.replace(hour=23, minute=59, second=59)
        conditions.append("data_hora_registro <= %(end_date)s")
        params['end_date'] = end_date_inclusive.strftime("%Y-%m-%d %H:%M:%S")
    if filter_remetente_nome:
        conditions.append("remetente_nome LIKE %(rem_nome)s")
        params['rem_nome'] = f"%{filter_remetente_nome}%"
    if filter_destinatario_nome:
        conditions.append("destinatario_nome LIKE %(dest_nome)s")
        params['dest_nome'] = f"%{filter_destinatario_nome}%"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY data_hora_registro DESC"
    try:
        # <<< ALTERAÇÃO AQUI >>>
        conn.commit()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        historico = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error as e:
        _get_show_message_func()("error", "Erro Leitura Histórico DB", f"Erro ao ler histórico de entradas do MySQL: {e}")
    return historico

def salvar_saida_db(dados_saida_completo):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO saidas (codigo_envelope, data_hora_registro_original, remetente_nome,
                                  remetente_telefone, destinatario_nome, destinatario_telefone,
                                  modalidade, atendente_registro_original, tipo_pacote,
                                  data_hora_saida, atendente_saida)
            VALUES (%(codigo_envelope)s, %(data_hora_registro_original)s, %(remetente_nome)s,
                    %(remetente_telefone)s, %(destinatario_nome)s, %(destinatario_telefone)s,
                    %(modalidade)s, %(atendente_registro_original)s, %(tipo_pacote)s,
                    %(data_hora_saida)s, %(atendente_saida)s)
        """
        cursor.execute(sql, dados_saida_completo)
        conn.commit()
        cursor.close()
        return True
    except mysql.connector.Error as e:
        _get_show_message_func()("error", "Erro Salvar Saída DB", f"Erro ao salvar saída no MySQL: {e}")
        conn.rollback()
        return False

def buscar_envelopes_para_saida(nome_dest_busca, show_message_func):
    show_message = show_message_func 
    conn = get_db_connection()
    if not conn:
        show_message("error", "Erro DB", "Não foi possível conectar ao MySQL para buscar envelopes.")
        return []
    envios_pendentes = []
    try:
        # <<< ALTERAÇÃO AQUI >>>
        conn.commit()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT e.* FROM entradas e
            LEFT JOIN saidas s ON e.codigo = s.codigo_envelope
            WHERE e.destinatario_nome = %s AND s.codigo_envelope IS NULL
            ORDER BY e.data_hora_registro DESC
        """
        cursor.execute(query, (nome_dest_busca,))
        envios_pendentes = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error as e:
        show_message("error", "Erro Busca Pendentes DB", f"Erro ao buscar envelopes pendentes no MySQL: {e}")
        return []
    return envios_pendentes

def ler_historico_saidas_db(filter_destinatario_nome=None, filter_start_date=None, filter_end_date=None):
    historico = []
    conn = get_db_connection()
    if not conn: return historico
    query = "SELECT * FROM saidas"
    conditions = []; params = {}
    if filter_destinatario_nome:
        conditions.append("destinatario_nome LIKE %(dest_nome)s")
        params['dest_nome'] = f"%{filter_destinatario_nome}%"
    if filter_start_date:
        conditions.append("data_hora_saida >= %(start_date)s")
        params['start_date'] = filter_start_date.strftime("%Y-%m-%d %H:%M:%S")
    if filter_end_date:
        end_date_inclusive = filter_end_date.replace(hour=23, minute=59, second=59)
        conditions.append("data_hora_saida <= %(end_date)s")
        params['end_date'] = end_date_inclusive.strftime("%Y-%m-%d %H:%M:%S")
    if conditions: query += " WHERE " + " AND ".join(conditions) 
    query += " ORDER BY data_hora_saida DESC"
    try:
        # <<< ALTERAÇÃO AQUI >>>
        conn.commit()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        historico = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error as e:
        _get_show_message_func()("error", "Erro Leitura Hist. Saídas DB", f"Erro ao ler histórico de saídas do MySQL: {e}")
    return historico

def ler_creditos_db():
    creditos = []
    conn = get_db_connection()
    if not conn: return creditos
    try:
        # <<< ALTERAÇÃO AQUI >>>
        conn.commit()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT nome, ncliente FROM clientes WHERE ncliente IS NOT NULL ORDER BY nome")
        creditos = cursor.fetchall()
        cursor.close()
    except mysql.connector.Error as e:
        _get_show_message_func()("error", "Erro Leitura Créditos DB", f"Erro ao ler créditos do MySQL: {e}")
    return creditos

def salvar_credito_db(nome, ncliente):
    show_message = _get_show_message_func()
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM clientes WHERE nome = %s", (nome,))
        result = cursor.fetchone()
        if result:
            sql = "UPDATE clientes SET ncliente = %s WHERE nome = %s"
            cursor.execute(sql, (ncliente, nome))
            conn.commit()
            cursor.close()
            show_message("info", "Sucesso", f"NCliente '{ncliente}' atribuído/atualizado para '{nome}'.")
            return True
        else:
            show_message("error", "Erro", f"Cliente '{nome}' não encontrado. Cadastre o cliente primeiro na aba 'Cadastro'.")
            conn.rollback()
            return False
    except mysql.connector.IntegrityError as e_int:
        show_message("error", "Erro DB", f"Erro de integridade ao salvar crédito '{nome}'. NCliente '{ncliente}' já existe para outro cliente. {e_int}")
        conn.rollback()
        return False
    except mysql.connector.Error as e:
        show_message("error", "Erro Salvar Crédito DB", f"Erro ao salvar crédito no MySQL: {e}")
        conn.rollback()
        return False

def remover_credito_db(ncliente):
    show_message = _get_show_message_func()
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        sql = "UPDATE clientes SET ncliente = NULL WHERE ncliente = %s"
        cursor.execute(sql, (ncliente,))
        conn.commit()
        cursor.close()
        if cursor.rowcount > 0:
            show_message("info", "Sucesso", f"NCliente '{ncliente}' removido do cliente associado.")
            return True
        else:
            show_message("warning", "Aviso", f"NCliente '{ncliente}' não encontrado para remoção.")
            return False
    except mysql.connector.Error as e:
        show_message("error", "Erro Remover Crédito DB", f"Erro ao remover crédito do MySQL: {e}")
        conn.rollback()
        return False

def close_db_connection():
    global db_conn
    if db_conn and db_conn.is_connected():
        db_conn.close()
        db_conn = None