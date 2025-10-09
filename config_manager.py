# config_manager.py
import configparser
import os
import sys
import threading
from tkinter import messagebox

# Mapeamento de nomes de variáveis globais para chaves no config.ini
COLOR_CONFIG_MAP = {
    "COR_FUNDO_JANELA": "cor_fundo_janela",
    "COR_FUNDO_FRAME": "cor_fundo_frame",
    "COR_TEXTO_GERAL": "cor_texto_geral",
    "COR_ENTRADA_BG": "cor_entrada_bg",
    "COR_ENTRADA_FG": "cor_entrada_fg",
    "COR_BOTAO_PRIMARIO_BG": "cor_botao_primario_bg",
    "COR_BOTAO_PRIMARIO_FG": "cor_botao_primario_fg",
    "COR_BOTAO_PRIMARIO_HOVER": "cor_botao_primario_hover",
    "COR_BOTAO_SECUNDARIO_BG": "cor_botao_secundario_bg",
    "COR_BOTAO_SECUNDARIO_FG": "cor_botao_secundario_fg",
    "COR_BOTAO_SECUNDARIO_HOVER": "cor_botao_secundario_hover",
    "COR_BOTAO_PERIGO_BG": "cor_botao_perigo_bg",
    "COR_BOTAO_PERIGO_FG": "cor_botao_perigo_fg",
    "COR_BOTAO_PERIGO_HOVER": "cor_botao_perigo_hover",
    "COR_TREEVIEW_HEADING_BG": "cor_treeview_heading_bg",
    "COR_TREEVIEW_HEADING_FG": "cor_treeview_heading_fg",
    "COR_TREEVIEW_ROW_BG": "cor_treeview_row_bg",
    "COR_TREEVIEW_ROW_FG": "cor_treeview_row_fg",
    "COR_TREEVIEW_SELECTED_BG": "cor_treeview_selected_bg",
    "COR_TREEVIEW_SELECTED_FG": "cor_treeview_selected_fg",
    "COR_ABA_SELECIONADA_BG": "cor_aba_selecionada_bg",
    "COR_ABA_SELECIONADA_FG": "cor_aba_selecionada_fg",
    "COR_ABA_NAO_SELECIONADA_BG": "cor_aba_nao_selecionada_bg",
    "COR_ABA_NAO_SELECIONADA_FG": "cor_aba_nao_selecionada_fg",
    "COR_LABELFRAME_FG": "cor_labelframe_fg"
}

CONFIG_FILE_NAME = "config.ini"

def _parse_list_from_config_string(config_string):
    if not config_string:
        return []
    return [item.strip() for item in config_string.split(',') if item.strip()]

def get_default_configs():
    return {
        "DatabaseMySQL": {
            "host": "localhost", "port": "3306", "user": "root",
            "password": "", "database": "gerenciador_envelopes_db"
        },
        "Printer": { "selected_printer": "", "enable_printing": "true" },
        "AppInfo": {
            "title_base": "Gerenciador de Envelopes", "title_local": "", "by_line": "by SamBr"
        },
        "Lists": {
            "modalidades": "Só entregar,Só receber",
            "atendentes": "Atendente A,Atendente B,Balcão",
            "atendentesb": "BOT-Atendente A,BOT-Atendente B,BOT-Balcão",
            "tipos_pacote": "Envelope,Caixa P,Caixa M,Caixa G,Tubo,Outro",
        },
        "PrintVisuals": {
            "font_size_dest_pts": "7", "font_size_code_pts": "20",
            "font_size_data_pts": "10", "line_spacing_mm": "1.0",
        },
        "Colors": {
            COLOR_CONFIG_MAP["COR_FUNDO_JANELA"]: "#F0F0F0",
            COLOR_CONFIG_MAP["COR_FUNDO_FRAME"]: "#E0E0E0",
            COLOR_CONFIG_MAP["COR_TEXTO_GERAL"]: "#000000",
            COLOR_CONFIG_MAP["COR_ENTRADA_BG"]: "#FFFFFF",
            COLOR_CONFIG_MAP["COR_ENTRADA_FG"]: "#000000",
            COLOR_CONFIG_MAP["COR_BOTAO_PRIMARIO_BG"]: "#0078D4",
            COLOR_CONFIG_MAP["COR_BOTAO_PRIMARIO_FG"]: "#FFFFFF",
            COLOR_CONFIG_MAP["COR_BOTAO_PRIMARIO_HOVER"]: "#005A9E",
            COLOR_CONFIG_MAP["COR_BOTAO_SECUNDARIO_BG"]: "#D0D0D0",
            COLOR_CONFIG_MAP["COR_BOTAO_SECUNDARIO_FG"]: "#000000",
            COLOR_CONFIG_MAP["COR_BOTAO_SECUNDARIO_HOVER"]: "#B0B0B0",
            COLOR_CONFIG_MAP["COR_BOTAO_PERIGO_BG"]: "#D32F2F",
            COLOR_CONFIG_MAP["COR_BOTAO_PERIGO_FG"]: "#FFFFFF",
            COLOR_CONFIG_MAP["COR_BOTAO_PERIGO_HOVER"]: "#B71C1C",
            COLOR_CONFIG_MAP["COR_TREEVIEW_HEADING_BG"]: "#E0E0E0",
            COLOR_CONFIG_MAP["COR_TREEVIEW_HEADING_FG"]: "#000000",
            COLOR_CONFIG_MAP["COR_TREEVIEW_ROW_BG"]: "#FFFFFF",
            COLOR_CONFIG_MAP["COR_TREEVIEW_ROW_FG"]: "#000000",
            COLOR_CONFIG_MAP["COR_TREEVIEW_SELECTED_BG"]: "#0078D4",
            COLOR_CONFIG_MAP["COR_TREEVIEW_SELECTED_FG"]: "#FFFFFF",
            COLOR_CONFIG_MAP["COR_ABA_SELECIONADA_BG"]: "#FFFFFF",
            COLOR_CONFIG_MAP["COR_ABA_SELECIONADA_FG"]: "#000000",
            COLOR_CONFIG_MAP["COR_ABA_NAO_SELECIONADA_BG"]: "#D0D0D0",
            COLOR_CONFIG_MAP["COR_ABA_NAO_SELECIONADA_FG"]: "#333333",
            COLOR_CONFIG_MAP["COR_LABELFRAME_FG"]: "#000000"
        }
    }

def ler_configuracoes(base_path):
    config_file_path = os.path.join(base_path, CONFIG_FILE_NAME)
    config = configparser.ConfigParser()
    default_configs = get_default_configs()
    
    # Dicionário para armazenar as configurações lidas/default para retorno
    # db_mysql_config e outras globais serão retornadas via este dicionário
    loaded_configs = {
        'db_mysql_config': {},
        'globals': {} # Para as outras variáveis globais
    }

    try:
        if os.path.exists(config_file_path):
            config.read(config_file_path, encoding='utf-8')

            if not config.has_section('Colors'):
                config.add_section('Colors')

            # Carregar configurações do banco de dados
            loaded_configs['db_mysql_config']['host'] = config.get('DatabaseMySQL', 'host', fallback=default_configs["DatabaseMySQL"]["host"])
            loaded_configs['db_mysql_config']['port'] = config.getint('DatabaseMySQL', 'port', fallback=int(default_configs["DatabaseMySQL"]["port"]))
            loaded_configs['db_mysql_config']['user'] = config.get('DatabaseMySQL', 'user', fallback=default_configs["DatabaseMySQL"]["user"])
            loaded_configs['db_mysql_config']['password'] = config.get('DatabaseMySQL', 'password', fallback=default_configs["DatabaseMySQL"]["password"])
            loaded_configs['db_mysql_config']['database'] = config.get('DatabaseMySQL', 'database', fallback=default_configs["DatabaseMySQL"]["database"])

            # Carregar configurações da impressora
            loaded_configs['globals']['selected_printer_name'] = config.get('Printer', 'selected_printer', fallback=default_configs["Printer"]["selected_printer"])
            loaded_configs['globals']['g_enable_printing'] = config.getboolean('Printer', 'enable_printing', fallback=default_configs["Printer"]["enable_printing"] == "true")

            # Carregar informações do aplicativo
            loaded_configs['globals']['app_title_base'] = config.get('AppInfo', 'title_base', fallback=default_configs["AppInfo"]["title_base"])
            loaded_configs['globals']['app_title_local'] = config.get('AppInfo', 'title_local', fallback=default_configs["AppInfo"]["title_local"])
            loaded_configs['globals']['app_by_line'] = config.get('AppInfo', 'by_line', fallback=default_configs["AppInfo"]["by_line"])

            # Carregar listas
            loaded_configs['globals']['lista_modalidades'] = _parse_list_from_config_string(config.get('Lists', 'modalidades', fallback=default_configs["Lists"]["modalidades"]))
            loaded_configs['globals']['lista_atendentes'] = _parse_list_from_config_string(config.get('Lists', 'atendentes', fallback=default_configs["Lists"]["atendentes"]))
            loaded_configs['globals']['lista_tipos_pacote'] = _parse_list_from_config_string(config.get('Lists', 'tipos_pacote', fallback=default_configs["Lists"]["tipos_pacote"]))
            loaded_configs['globals']['lista_atendentesb'] = _parse_list_from_config_string(config.get('Lists', 'atendentesb', fallback=default_configs["Lists"]["atendentesb"]))
            
            # Garantir que as listas não fiquem vazias se o fallback não funcionar
            if not loaded_configs['globals']['lista_modalidades']: loaded_configs['globals']['lista_modalidades'] = _parse_list_from_config_string(default_configs["Lists"]["modalidades"])
            if not loaded_configs['globals']['lista_atendentes']: loaded_configs['globals']['lista_atendentes'] = _parse_list_from_config_string(default_configs["Lists"]["atendentes"])
            if not loaded_configs['globals']['lista_tipos_pacote']: loaded_configs['globals']['lista_tipos_pacote'] = _parse_list_from_config_string(default_configs["Lists"]["tipos_pacote"])
            if not loaded_configs['globals']['lista_atendentesb']: loaded_configs['globals']['lista_atendentesb'] = _parse_list_from_config_string(default_configs["Lists"]["atendentesb"])
            
            # Carregar configurações visuais de impressão
            loaded_configs['globals']['g_font_size_dest_pts'] = config.getint('PrintVisuals', 'font_size_dest_pts', fallback=int(default_configs["PrintVisuals"]["font_size_dest_pts"]))
            loaded_configs['globals']['g_font_size_code_pts'] = config.getint('PrintVisuals', 'font_size_code_pts', fallback=int(default_configs["PrintVisuals"]["font_size_code_pts"]))
            loaded_configs['globals']['g_font_size_data_pts'] = config.getint('PrintVisuals', 'font_size_data_pts', fallback=int(default_configs["PrintVisuals"]["font_size_data_pts"]))
            loaded_configs['globals']['g_line_spacing_mm'] = config.getfloat('PrintVisuals', 'line_spacing_mm', fallback=float(default_configs["PrintVisuals"]["line_spacing_mm"]))

            # Carregar cores
            for var_name, key_name in COLOR_CONFIG_MAP.items():
                loaded_configs['globals'][var_name] = config.get('Colors', key_name, fallback=default_configs["Colors"][key_name])

        else:
            print(f"INFO: Arquivo '{CONFIG_FILE_NAME}' não encontrado. Criando com valores padrão.")
            # Usar defaults
            loaded_configs['db_mysql_config'] = default_configs["DatabaseMySQL"].copy()
            loaded_configs['db_mysql_config']['port'] = int(loaded_configs['db_mysql_config']['port']) # Ensure port is int
            
            loaded_configs['globals']['selected_printer_name'] = default_configs["Printer"]["selected_printer"]
            loaded_configs['globals']['g_enable_printing'] = default_configs["Printer"]["enable_printing"] == "true"
            loaded_configs['globals']['app_title_base'] = default_configs["AppInfo"]["title_base"]
            loaded_configs['globals']['app_title_local'] = default_configs["AppInfo"]["title_local"]
            loaded_configs['globals']['app_by_line'] = default_configs["AppInfo"]["by_line"]
            loaded_configs['globals']['lista_modalidades'] = _parse_list_from_config_string(default_configs["Lists"]["modalidades"])
            loaded_configs['globals']['lista_atendentes'] = _parse_list_from_config_string(default_configs["Lists"]["atendentes"])
            loaded_configs['globals']['lista_atendentesb'] = _parse_list_from_config_string(default_configs["Lists"]["atendentesb"])
            loaded_configs['globals']['lista_tipos_pacote'] = _parse_list_from_config_string(default_configs["Lists"]["tipos_pacote"])
            loaded_configs['globals']['g_font_size_dest_pts'] = int(default_configs["PrintVisuals"]["font_size_dest_pts"])
            loaded_configs['globals']['g_font_size_code_pts'] = int(default_configs["PrintVisuals"]["font_size_code_pts"])
            loaded_configs['globals']['g_font_size_data_pts'] = int(default_configs["PrintVisuals"]["font_size_data_pts"])
            loaded_configs['globals']['g_line_spacing_mm'] = float(default_configs["PrintVisuals"]["line_spacing_mm"])

            for var_name, key_name in COLOR_CONFIG_MAP.items():
                loaded_configs['globals'][var_name] = default_configs["Colors"][key_name]
            
            # Salvar as configurações padrão recém-criadas
            salvar_configuracoes_completas(base_path, default_configs)

    except Exception as e:
        # Tenta usar messagebox se a janela principal já estiver disponível
        # Caso contrário, apenas imprime no console
        try:
            # Importar a função show_message_thread_safe do ui_manager para evitar circular import
            from ui_manager import show_message_thread_safe
            show_message_thread_safe("error", "Erro Config", f"Falha ao ler '{config_file_path}': {e}.\nUsando padrões e tentando recriar.")
        except ImportError:
            print(f"ERROR: Falha ao ler '{config_file_path}': {e}.\nUsando padrões e tentando recriar.")

        # Recarregar com defaults em caso de erro
        loaded_configs['db_mysql_config'] = default_configs["DatabaseMySQL"].copy()
        loaded_configs['db_mysql_config']['port'] = int(loaded_configs['db_mysql_config']['port'])

        loaded_configs['globals']['selected_printer_name'] = default_configs["Printer"]["selected_printer"]
        loaded_configs['globals']['g_enable_printing'] = default_configs["Printer"]["enable_printing"] == "true"
        loaded_configs['globals']['app_title_base'] = default_configs["AppInfo"]["title_base"]
        loaded_configs['globals']['app_title_local'] = default_configs["AppInfo"]["title_local"]
        loaded_configs['globals']['app_by_line'] = default_configs["AppInfo"]["by_line"]
        loaded_configs['globals']['lista_modalidades'] = _parse_list_from_config_string(default_configs["Lists"]["modalidades"])
        loaded_configs['globals']['lista_atendentes'] = _parse_list_from_config_string(default_configs["Lists"]["atendentes"])
        loaded_configs['globals']['lista_atendentesb'] = _parse_list_from_config_string(default_configs["Lists"]["atendentesb"])
        loaded_configs['globals']['lista_tipos_pacote'] = _parse_list_from_config_string(default_configs["Lists"]["tipos_pacote"])
        loaded_configs['globals']['g_font_size_dest_pts'] = int(default_configs["PrintVisuals"]["font_size_dest_pts"])
        loaded_configs['globals']['g_font_size_code_pts'] = int(default_configs["PrintVisuals"]["font_size_code_pts"])
        loaded_configs['globals']['g_font_size_data_pts'] = int(default_configs["PrintVisuals"]["font_size_data_pts"])
        loaded_configs['globals']['g_line_spacing_mm'] = float(default_configs["PrintVisuals"]["line_spacing_mm"])

        for var_name, key_name in COLOR_CONFIG_MAP.items():
            loaded_configs['globals'][var_name] = default_configs["Colors"][key_name]

        salvar_configuracoes_completas(base_path, default_configs)

    return loaded_configs


def salvar_configuracoes_completas(base_path, config_dict):
    config_file_path = os.path.join(base_path, CONFIG_FILE_NAME)
    config = configparser.ConfigParser()
    for section, options in config_dict.items():
        config[section] = options
    try:
        with open(config_file_path, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        return True
    except Exception as e:
        try:
            from ui_manager import show_message_thread_safe
            show_message_thread_safe("error", "Erro Salvar Config", f"Falha ao salvar {config_file_path}: {e}")
        except ImportError:
            print(f"ERROR: Falha ao salvar {config_file_path}: {e}")
        return False

def salvar_configuracoes_atuais_para_arquivo(global_state, color_config_map_ref):
    """
    Salva as configurações atuais (do estado global) para o arquivo config.ini.
    Recebe o dicionário global_state e o mapeamento de cores para construir os dados.
    """
    # A base_path precisa ser obtida de forma consistente
    # Uma forma é passar main.APP_BASE_PATH para cá, ou o main.py chamar essa função.
    # Por simplicidade, vamos obter aqui, mas o ideal seria ser injetado.
    from utils import get_base_path
    base_path = get_base_path()

    current_colors_config = {}
    for var_name, key_name in color_config_map_ref.items():
        if var_name in global_state:
            current_colors_config[key_name] = global_state[var_name]
        else: # Fallback para defaults caso a variável não esteja no global_state
            current_colors_config[key_name] = get_default_configs()["Colors"].get(key_name, "#000000") # Default fallback

    current_config_data = {
        "DatabaseMySQL": {
            "host": global_state['db_mysql_config'].get('host', 'localhost'),
            "port": str(global_state['db_mysql_config'].get('port', 3306)),
            "user": global_state['db_mysql_config'].get('user', 'root'),
            "password": global_state['db_mysql_config'].get('password', ''),
            "database": global_state['db_mysql_config'].get('database', 'gerenciador_envelopes_db'),
        },
        "Printer": {
            "selected_printer": global_state.get('selected_printer_name', ''),
            "enable_printing": str(global_state.get('g_enable_printing', True)).lower(),
        },
        "AppInfo": {
            "title_base": global_state.get('app_title_base', 'Gerenciador de Envelopes'),
            "title_local": global_state.get('app_title_local', ''),
            "by_line": global_state.get('app_by_line', 'by SamBr'),
        },
        "Lists": {
            "modalidades": ",".join(global_state.get('lista_modalidades', [])),
            "atendentes": ",".join(global_state.get('lista_atendentes', [])),
            "atendentesb": ",".join(global_state.get('lista_atendentesb', [])),
            "tipos_pacote": ",".join(global_state.get('lista_tipos_pacote', [])),
        },
        "PrintVisuals": {
            "font_size_dest_pts": str(global_state.get('g_font_size_dest_pts', 7)),
            "font_size_code_pts": str(global_state.get('g_font_size_code_pts', 20)),
            "font_size_data_pts": str(global_state.get('g_font_size_data_pts', 10)),
            "line_spacing_mm": str(global_state.get('g_line_spacing_mm', 1.0)),
        },
        "Colors": current_colors_config
    }
    return salvar_configuracoes_completas(base_path, current_config_data)