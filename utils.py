# utils.py
import datetime
import random
import unicodedata
import os
import sys
import threading
import traceback
import socket
import requests
import json
# Adicionado para a URL do WhatsApp
import urllib.parse 
# Adicionado para abrir o navegador
import webbrowser 

# Importar ler_configuracoes e get_base_path de config_manager e utils
from config_manager import ler_configuracoes


PYWIN32_AVAILABLE = False
try:
    import win32print
    import win32ui
    import win32gui
    import win32con
    PYWIN32_AVAILABLE = True
except ImportError:
    pass

# --- NOVA FUNÇÃO ---
def formatar_mensagem_whatsapp(nome_local, destinatario_nome, remetente_nome, codigo):
    """Formata a mensagem padrão de notificação do WhatsApp."""
    return (
        f"Olá, {destinatario_nome}! 👋\n\n"
        f"Temos uma nova correspondência para você na recepção da {nome_local}, "
        f"deixada por {remetente_nome}.\n\n"
        f"🏷️ O código de retirada é: *{codigo}*\n\n"
        "Por favor, apresente este código na recepção para retirar seu envelope.\n\n"
        "Atenciosamente,\n"
        f"Recepção {nome_local}"
    )

# --- ALTERAÇÃO 1: Adicionar um codificador customizado para datas ---
class DateTimeEncoder(json.JSONEncoder):
    """
    Codificador JSON customizado que sabe como converter objetos datetime para strings.
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            # Converte o objeto datetime para uma string no formato ISO 8601
            return obj.isoformat()
        # Para qualquer outro tipo, usa o comportamento padrão
        return json.JSONEncoder.default(self, obj)


# --- FUNÇÃO DE WEBHOOK ---
def enviar_notificacao_via_bot(evento_data):
    """
    Envia uma notificação para o bot de WhatsApp via webhook.
    O bot deve estar rodando e escutando na porta 3000 no IP configurado.
    """
    try:
        from ui_manager import show_message_thread_safe
    except ImportError:
        show_message_thread_safe = lambda msg_type, title, message: print(f"UTILS_MSG_ERROR ({msg_type}) {title}: {message}")

    # Obter o caminho base para ler o config.ini
    base_path = get_base_path()
    
    # Ler as configurações para obter o host do Raspberry Pi
    configs = ler_configuracoes(base_path)
    raspberry_pi_host = configs['db_mysql_config']['host']
    
    # Definir a URL do webhook usando o IP do Raspberry Pi
    url = f"http://{raspberry_pi_host}:3000/webhook/envelope"
    headers = {'Content-Type': 'application/json'}
    
    try:
        # --- ALTERAÇÃO 2: Usar o codificador customizado ao converter para JSON ---
        json_payload = json.dumps(evento_data, cls=DateTimeEncoder)
        
        response = requests.post(url, data=json_payload, headers=headers, timeout=5)
        
        if response.status_code == 200:
            print(f"✅ Notificação enviada com sucesso para o bot em {raspberry_pi_host}: {evento_data.get('tipo_evento')}")
            return True
        else:
            print(f"❌ Falha ao enviar notificação para o bot em {raspberry_pi_host}. Status: {response.status_code}, Resposta: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão ao tentar enviar notificação para o bot em {raspberry_pi_host}: {e}")
        return False

# O restante do arquivo continua igual...

def _python_muldiv(nNumber, nNumerator, nDenominator):
    if nDenominator == 0: return 0
    return int((nNumber * nNumerator + nDenominator // 2) // nDenominator)

def get_base_path():
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base_path = os.path.dirname(sys.executable)
    elif getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return base_path

def parse_flexible_date(date_str, primary_format, alternative_formats):
    if not date_str: return None
    formats_to_try = [primary_format] + alternative_formats
    for fmt in formats_to_try:
        try: return datetime.datetime.strptime(date_str, fmt)
        except (ValueError, TypeError): continue
    return None

def parse_user_date(date_str):
    if not date_str: return None
    try: return datetime.datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        try:
            from ui_manager import show_message_thread_safe
            show_message_thread_safe("error", "Erro de Data", f"Formato de data inválido: '{date_str}'. Use dd/mm/aaaa.")
        except ImportError:
            print(f"ERROR: Formato de data inválido: '{date_str}'. Use dd/mm/aaaa.")
        return None

def gerar_codigo(destinatario):
    if not destinatario:
        inicial = 'X'
    else:
        try:
            dest_sem_acento = ''.join(c for c in unicodedata.normalize('NFD', destinatario) if unicodedata.category(c) != 'Mn')
            inicial = dest_sem_acento[0].upper() if dest_sem_acento else 'X'
        except:
            inicial = destinatario[0].upper() if destinatario else 'X'
    caracteres = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    codigo_aleatorio = ''.join(random.choice(caracteres) for _ in range(4))
    return f"{inicial}{codigo_aleatorio}"

def enviar_whatsapp_geral(telefone, mensagem_texto):
    """Abre o WhatsApp Web para enviar uma mensagem."""
    try:
        from ui_manager import show_message_thread_safe
    except ImportError:
        show_message_thread_safe = lambda msg_type, title, message: print(f"UTILS_MSG_ERROR ({msg_type}) {title}: {message}")

    if not telefone or telefone == "N/A": return False
    telefone_limpo = ''.join(filter(str.isdigit, str(telefone)))
    if len(telefone_limpo) < 10: return False
    mensagem_encodada = urllib.parse.quote(mensagem_texto)
    if not telefone_limpo.startswith("55") and (10 <= len(telefone_limpo) <= 11):
        url = f"https://web.whatsapp.com/send/?phone=55{telefone_limpo}&text={mensagem_encodada}"
    else:
        url = f"https://web.whatsapp.com/send/?phone={telefone_limpo}&text={mensagem_encodada}"
    try:
        webbrowser.open(url)
        return True
    except Exception as e:
        show_message_thread_safe("error", "Erro WhatsApp", f"Falha ao abrir link do WhatsApp para {telefone_limpo}: {e}")
        return False

def imprimir_etiqueta_direto_windows(printer_name_cfg, destinatario_nome, codigo_envelope, data_hora_obj,
                                    g_font_size_dest_pts, g_font_size_code_pts, g_font_size_data_pts, g_line_spacing_mm):
    """Imprime uma etiqueta diretamente para a impressora Windows."""
    try:
        from ui_manager import show_message_thread_safe
    except ImportError:
        show_message_thread_safe = lambda msg_type, title, message: print(f"UTILS_MSG_ERROR ({msg_type}) {title}: {message}")

    if not PYWIN32_AVAILABLE:
        show_message_thread_safe("error", "Erro de Impressão", "A biblioteca pywin32 é necessária para impressão e não foi encontrada.")
        return False
    if not printer_name_cfg:
        show_message_thread_safe("error", "Erro de Impressão", "Nenhuma impressora selecionada nas configurações.")
        return False

    dest_text = f"Dest.: {destinatario_nome or 'N/D'}"
    code_text = str(codigo_envelope or "N/D CÓDIGO")
    date_text = data_hora_obj.strftime("%d/%m/%y às %H:%M") if data_hora_obj else "Data Indisponível"

    h_printer = None
    pdc_obj = None
    try:
        h_printer = win32print.OpenPrinter(printer_name_cfg)
        pdc = win32ui.CreateDC()
        pdc.CreatePrinterDC(printer_name_cfg)
        pdc_obj = pdc

        dpi_x = pdc.GetDeviceCaps(win32con.LOGPIXELSX)
        dpi_y = pdc.GetDeviceCaps(win32con.LOGPIXELSY)
        
        LABEL_WIDTH_MM = 62
        LABEL_HEIGHT_MM = 29
        LABEL_PRINT_LEFT_MARGIN_MM = 1
        LABEL_PRINT_TOP_MARGIN_MM = 2
        LABEL_PRINT_FONT_NAME = "Arial"

        left_margin_dots = int(LABEL_PRINT_LEFT_MARGIN_MM * dpi_x / 25.4)
        top_margin_dots = int(LABEL_PRINT_TOP_MARGIN_MM * dpi_y / 25.4)
        printable_width_dots = int((LABEL_WIDTH_MM - 2 * LABEL_PRINT_LEFT_MARGIN_MM) * dpi_x / 25.4)
        line_spacing_dots = int(g_line_spacing_mm * dpi_y / 25.4)

        pdc.StartDoc(f"Etiqueta-{codigo_envelope}")
        pdc.StartPage()

        font_dest_height = -_python_muldiv(g_font_size_dest_pts, dpi_y, 72)
        font_code_height = -_python_muldiv(g_font_size_code_pts, dpi_y, 72)
        font_data_height = -_python_muldiv(g_font_size_data_pts, dpi_y, 72)

        font_dest = win32ui.CreateFont({'name': LABEL_PRINT_FONT_NAME, 'height': font_dest_height, 'weight': win32con.FW_NORMAL})
        font_code = win32ui.CreateFont({'name': LABEL_PRINT_FONT_NAME, 'height': font_code_height, 'weight': win32con.FW_BOLD})
        font_data = win32ui.CreateFont({'name': LABEL_PRINT_FONT_NAME, 'height': font_data_height, 'weight': win32con.FW_NORMAL})

        current_y = top_margin_dots
        pdc.SelectObject(font_dest)
        text_width_pixels, text_height_pixels_dest = pdc.GetTextExtent(dest_text)
        x_pos_dest = left_margin_dots + (printable_width_dots - text_width_pixels) // 2
        if x_pos_dest < left_margin_dots: x_pos_dest = left_margin_dots
        pdc.TextOut(x_pos_dest, current_y, dest_text)
        current_y += text_height_pixels_dest + line_spacing_dots

        pdc.SelectObject(font_code)
        text_width_pixels, text_height_pixels_code = pdc.GetTextExtent(code_text)
        x_pos_code = left_margin_dots + (printable_width_dots - text_width_pixels) // 2
        if x_pos_code < left_margin_dots: x_pos_code = left_margin_dots
        pdc.TextOut(x_pos_code, current_y, code_text)
        current_y += text_height_pixels_code + line_spacing_dots

        pdc.SelectObject(font_data)
        text_width_pixels, text_height_pixels_data = pdc.GetTextExtent(date_text)
        x_pos_data = left_margin_dots + (printable_width_dots - text_width_pixels) // 2
        if x_pos_data < left_margin_dots: x_pos_data = left_margin_dots
        pdc.TextOut(x_pos_data, current_y, date_text)

        pdc.EndPage()
        pdc.EndDoc()
        return True
    except Exception as e:
        tb_str = traceback.format_exc()
        show_message_thread_safe("error", "Erro de Impressão", f"Falha ao imprimir a etiqueta em '{printer_name_cfg}':\n{e}\n\nDetalhes:\n{tb_str}\\n\\nVerifique as configurações da impressora, o tamanho da etiqueta e se ela está online.")
        if pdc_obj:
            try: pdc_obj.EndDoc()
            except Exception: pass
        return False
    finally:
        if h_printer:
            win32print.ClosePrinter(h_printer)
        if pdc_obj:
            try: pdc_obj.DeleteDC()
            except: pass


def listar_impressoras_windows():
    """Lista as impressoras instaladas no sistema Windows."""
    try:
        from ui_manager import show_message_thread_safe
    except ImportError:
        show_message_thread_safe = lambda msg_type, title, message: print(f"UTILS_MSG_ERROR ({msg_type}) {title}: {message}")

    if not PYWIN32_AVAILABLE: return ["pywin32 não instalado"]
    try:
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
        return sorted([printer[2] for printer in printers])
    except Exception as e:
        show_message_thread_safe("error", "Erro ao Listar Impressoras", f"Erro ao listar impressoras: {e}")
        return ["Erro ao listar impressoras"]

def get_local_ipv4():
    """Tenta obter o endereço IPv4 local da máquina."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except Exception:
        return "127.0.0.1"