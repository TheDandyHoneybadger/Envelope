# main_servidor.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel, Label, Entry, Button
import sys
import os
import threading
import time

# Importar dos módulos customizados
import config_manager
import database_manager
import utils

# Módulos de UI refatorados
import ui_manager
import ui_helpers 
import ui_event_handlers

# Mapeamento de nomes de variáveis globais para chaves no config.ini
from config_manager import COLOR_CONFIG_MAP

# --- Variáveis Globais de Configuração e Cache ---
db_mysql_config_global = {}
app_globals = {}
_clientes_cache = None
_cache_timestamp = 0
CACHE_DURATION_SECONDS = 30 # Cache válido por 30 segundos

# --- Funções de Cache ---
def ler_clientes_com_cache():
    """
    Wrapper para database_manager.ler_clientes que adiciona uma camada de cache.
    """
    global _clientes_cache, _cache_timestamp
    agora = time.time()
    
    # Se o cache existe e ainda é válido, retorna os dados cacheados
    if _clientes_cache is not None and (agora - _cache_timestamp < CACHE_DURATION_SECONDS):
        return _clientes_cache
    
    # Caso contrário, busca no banco de dados, atualiza o cache e o timestamp
    _clientes_cache = database_manager.ler_clientes()
    _cache_timestamp = agora
    return _clientes_cache

def invalidar_cache_clientes():
    """Força a invalidação do cache de clientes, para ser usado após uma atualização."""
    global _clientes_cache
    _clientes_cache = None
    print("[CACHE] Cache de clientes invalidado.")

def salvar_cliente_e_invalidar_cache(*args, **kwargs):
    """
    Wrapper para database_manager.salvar_cliente que invalida o cache em caso de sucesso.
    """
    sucesso = database_manager.salvar_cliente(*args, **kwargs)
    if sucesso:
        invalidar_cache_clientes()
    return sucesso

def deletar_cliente_e_invalidar_cache(*args, **kwargs):
    """
    Wrapper para database_manager.deletar_cliente que invalida o cache em caso de sucesso.
    """
    sucesso = database_manager.deletar_cliente(*args, **kwargs)
    if sucesso:
        invalidar_cache_clientes()
    return sucesso

def main():
    """Função principal que inicializa e executa a aplicação."""
    global db_mysql_config_global, app_globals

    # 1. Inicializa a janela principal do Tkinter (mas a mantém oculta)
    janela = tk.Tk()
    janela.withdraw()
    ui_manager.ui_elements['janela'] = janela

    # 2. Carregar configurações do arquivo config.ini
    base_path = utils.get_base_path()
    config_data = config_manager.ler_configuracoes(base_path)
    db_mysql_config_global = config_data['db_mysql_config']
    app_globals = config_data['globals']

    # 3. Loop de tentativa de conexão com o banco de dados com UI de progresso
    while True:
        progress_dialog = Toplevel()
        progress_dialog.title("Inicializando")
        progress_dialog.geometry("300x100")
        # Centraliza a janela de progresso
        janela.update_idletasks()
        x = janela.winfo_x() + (janela.winfo_width() // 2) - (progress_dialog.winfo_width() // 2)
        y = janela.winfo_y() + (janela.winfo_height() // 2) - (progress_dialog.winfo_height() // 2)
        progress_dialog.geometry(f"+{x}+{y}")
        
        ttk.Label(progress_dialog, text="Conectando ao banco de dados...").pack(pady=10)
        progress_bar = ttk.Progressbar(progress_dialog, mode='indeterminate')
        progress_bar.pack(pady=10, padx=20, fill=tk.X)
        progress_bar.start(10)
        janela.update_idletasks()

        database_manager.set_db_config(db_mysql_config_global)
        conn = database_manager.init_db(ui_manager.show_message_thread_safe)
        
        progress_bar.stop()
        progress_dialog.destroy()

        if conn:
            break
        
        retry = messagebox.askretrycancel(
            "Erro de Conexão com o Banco de Dados",
            "Não foi possível conectar ao MySQL. Verifique se o servidor está rodando e as configurações em 'config.ini' estão corretas.\n\nDeseja tentar novamente?"
        )
        if not retry:
            janela.destroy()
            sys.exit(1)

    # 4. Preparar o estado global e os callbacks para a UI
    global_state = {
        'janela': janela,
        'db_mysql_config': db_mysql_config_global,
        'COLOR_CONFIG_MAP': COLOR_CONFIG_MAP,
        'PYWIN32_AVAILABLE': ui_manager.PYWIN32_AVAILABLE,
        'envios_exibidos_na_saida': [],
        'ultima_etiqueta_codigo': None,
        'ultima_etiqueta_data_hora': None,
        'ultima_etiqueta_destinatario_nome': None,
        'ultimo_atendente_entrada': ""
    }
    global_state.update(app_globals)

    ui_callbacks = {
        'ler_clientes': ler_clientes_com_cache,
        'salvar_cliente': salvar_cliente_e_invalidar_cache,
        'invalidar_cache_clientes': invalidar_cache_clientes,
        'deletar_cliente': deletar_cliente_e_invalidar_cache,
        'gerar_codigo': utils.gerar_codigo,
        'salvar_nova_entrada_db': database_manager.salvar_nova_entrada_db,
        'imprimir_etiqueta_direto_windows': utils.imprimir_etiqueta_direto_windows,
        'enviar_notificacao_via_bot': utils.enviar_notificacao_via_bot,
        'enviar_whatsapp_geral': utils.enviar_whatsapp_geral,
        'formatar_mensagem_whatsapp': utils.formatar_mensagem_whatsapp,
        'ler_historico_entradas_db': database_manager.ler_historico_entradas_db,
        'salvar_saida_db': database_manager.salvar_saida_db,
        'ler_historico_saidas_db': database_manager.ler_historico_saidas_db,
        'buscar_envelopes_para_saida': database_manager.buscar_envelopes_para_saida,
        'listar_impressoras_windows': utils.listar_impressoras_windows,
        'salvar_configuracoes_atuais_para_arquivo': config_manager.salvar_configuracoes_atuais_para_arquivo,
        'parse_user_date': utils.parse_user_date,
        'ler_creditos_db': database_manager.ler_creditos_db,
        'remover_credito_db': database_manager.remover_credito_db,
        'ler_programados_por_remetente': database_manager.ler_programados_por_remetente,
        'deletar_programado': database_manager.deletar_programado,
        'processar_envelope_programado': database_manager.processar_envelope_programado
    }

    # 5. Configurar e construir a UI
    ui_helpers.update_title_from_config(
        janela, 
        global_state.get('app_title_base', ''), 
        global_state.get('app_title_local', ''), 
        global_state.get('app_by_line', '')
    )
    janela.geometry("1300x850")

    colors_dict = {key: global_state[key] for key in COLOR_CONFIG_MAP if key in global_state}
    ui_manager.apply_dynamic_styles(janela, colors_dict)

    ui_manager.build_ui(janela, global_state, ui_callbacks)
    
    # 6. Definir estados iniciais dos widgets (sem carregar históricos aqui)
    janela.after(150, lambda: ui_manager.set_initial_widget_states(global_state, ui_callbacks))
    
    # 7. Exibir a janela e iniciar o loop principal
    janela.deiconify()
    janela.mainloop()

    # 8. Limpeza ao fechar
    database_manager.close_db_connection()

if __name__ == "__main__":
    APP_BASE_PATH = utils.get_base_path()
    if APP_BASE_PATH not in sys.path:
        sys.path.insert(0, APP_BASE_PATH)

    main()