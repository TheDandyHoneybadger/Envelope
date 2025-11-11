# ui_manager.py
import tkinter as tk
from tkinter import ttk, messagebox
import sys

# Módulos de UI refatorados
import ui_builder_tabs
import ui_event_handlers
import ui_helpers

# --- Variáveis Globais e Constantes ---
ui_elements = {}

PYWIN32_AVAILABLE = False
try:
    import win32print, win32ui, win32gui, win32con
    PYWIN32_AVAILABLE = True
except ImportError:
    pass

# --- Funções de Baixo Nível e Thread-Safe ---
def show_message_thread_safe(message_type, title, message):
    """Exibe uma messagebox de forma segura para threads."""
    if 'janela' in ui_elements and ui_elements['janela'].winfo_exists():
        if message_type == "error":
            ui_elements['janela'].after(0, lambda: messagebox.showerror(title, message))
        elif message_type == "warning":
            ui_elements['janela'].after(0, lambda: messagebox.showwarning(title, message))
        elif message_type == "info":
            ui_elements['janela'].after(0, lambda: messagebox.showinfo(title, message))
        elif message_type == "askyesno":
            return messagebox.askyesno(title, message)
    else:
        print(f"TK_MSG_FALLBACK ({message_type.upper()}) {title}: {message}")
        if message_type == "askyesno": return False

# --- Estilização ---
def apply_dynamic_styles(janela_ref, colors):
    """Aplica os estilos dinâmicos aos widgets ttk."""
    ui_elements['colors'] = colors
    style = ttk.Style(janela_ref)
    try:
        if 'clam' in style.theme_names():
            style.theme_use('clam')
    except tk.TclError:
        print("Não foi possível aplicar o tema 'clam', usando o padrão do sistema.")

    BASE_FONT_FAMILY = "Segoe UI"
    BASE_FONT_SIZE = 9
    BOLD_FONT_SIZE = 10
    LABEL_FONT = (BASE_FONT_FAMILY, BASE_FONT_SIZE)
    ENTRY_FONT = (BASE_FONT_FAMILY, BASE_FONT_SIZE)
    BUTTON_FONT = (BASE_FONT_FAMILY, BASE_FONT_SIZE, "bold")
    TREEVIEW_HEADING_FONT = (BASE_FONT_FAMILY, BOLD_FONT_SIZE, "bold")
    TREEVIEW_ROW_FONT = (BASE_FONT_FAMILY, BASE_FONT_SIZE)
    TAB_FONT = (BASE_FONT_FAMILY, BASE_FONT_SIZE, "bold")
    LABELFRAME_FONT_STYLE = (BASE_FONT_FAMILY, BOLD_FONT_SIZE, "bold")
    
    style.configure('.', font=LABEL_FONT, foreground=colors["COR_TEXTO_GERAL"], background=colors["COR_FUNDO_JANELA"], highlightthickness=0)
    style.configure("TFrame", background=colors["COR_FUNDO_FRAME"])
    style.configure("Content.TFrame", background=colors["COR_FUNDO_FRAME"])
    style.configure("TLabel", font=LABEL_FONT, foreground=colors["COR_TEXTO_GERAL"], background=colors["COR_FUNDO_FRAME"])
    style.configure("Note.TLabel", font=(BASE_FONT_FAMILY, BASE_FONT_SIZE -1), foreground=colors["COR_TEXTO_GERAL"], background=colors["COR_FUNDO_FRAME"])
    style.configure("TEntry", font=ENTRY_FONT, fieldbackground=colors["COR_ENTRADA_BG"], foreground=colors["COR_ENTRADA_FG"], highlightthickness=0, borderwidth=1)
    style.configure("TCombobox", font=ENTRY_FONT, fieldbackground=colors["COR_ENTRADA_BG"], foreground=colors["COR_ENTRADA_FG"], highlightthickness=0)
    janela_ref.option_add('*TCombobox*Listbox.background', colors["COR_ENTRADA_BG"])
    janela_ref.option_add('*TCombobox*Listbox.foreground', colors["COR_ENTRADA_FG"])
    janela_ref.option_add('*TCombobox*Listbox.selectBackground', colors["COR_TREEVIEW_SELECTED_BG"])
    janela_ref.option_add('*TCombobox*Listbox.selectForeground', colors["COR_TREEVIEW_SELECTED_FG"])
    style.configure("TButton", font=BUTTON_FONT, padding=(8, 4), highlightthickness=0, borderwidth=0)
    style.configure("Primary.TButton", background=colors["COR_BOTAO_PRIMARIO_BG"], foreground=colors["COR_BOTAO_PRIMARIO_FG"])
    style.map("Primary.TButton", background=[('active', colors["COR_BOTAO_PRIMARIO_HOVER"])])
    style.configure("Secondary.TButton", background=colors["COR_BOTAO_SECUNDARIO_BG"], foreground=colors["COR_BOTAO_SECUNDARIO_FG"])
    style.map("Secondary.TButton", background=[('active', colors["COR_BOTAO_SECUNDARIO_HOVER"])])
    style.configure("Danger.TButton", background=colors["COR_BOTAO_PERIGO_BG"], foreground=colors["COR_BOTAO_PERIGO_FG"])
    style.map("Danger.TButton", background=[('active', colors["COR_BOTAO_PERIGO_HOVER"])])
    style.configure("Treeview.Heading", font=TREEVIEW_HEADING_FONT, background=colors["COR_TREEVIEW_HEADING_BG"], foreground=colors["COR_TREEVIEW_HEADING_FG"])
    style.configure("Treeview", rowheight=22, font=TREEVIEW_ROW_FONT, fieldbackground=colors["COR_TREEVIEW_ROW_BG"], background=colors["COR_TREEVIEW_ROW_BG"], foreground=colors["COR_TREEVIEW_ROW_FG"], highlightthickness=0, borderwidth=0)
    style.map("Treeview", background=[('selected', colors["COR_TREEVIEW_SELECTED_BG"])], foreground=[('selected', colors["COR_TREEVIEW_SELECTED_FG"])])
    style.configure("TNotebook.Tab", font=TAB_FONT, padding=[10, 5], highlightthickness=0)
    style.map("TNotebook.Tab", background=[("selected", colors["COR_ABA_SELECIONADA_BG"])], foreground=[("selected", colors["COR_ABA_SELECIONADA_FG"])])
    style.configure("TLabelframe", font=LABELFRAME_FONT_STYLE, background=colors["COR_FUNDO_FRAME"])
    style.configure("TLabelframe.Label", font=LABELFRAME_FONT_STYLE, foreground=colors["COR_LABELFRAME_FG"], background=colors["COR_FUNDO_FRAME"])

# --- Construção da UI Principal (Orquestrador) ---
def build_ui(janela_ref, global_state, ui_callbacks):
    """Constrói a interface do usuário chamando os builders de cada aba."""
    global ui_elements
    ui_elements['janela'] = janela_ref
    ui_elements['PYWIN32_AVAILABLE'] = PYWIN32_AVAILABLE
    
    notebook = ttk.Notebook(janela_ref, style="TNotebook")
    notebook.pack(expand=True, fill='both', padx=10, pady=10)
    ui_elements['notebook'] = notebook

    show_msg_func_ref = show_message_thread_safe

    aba_entrada = ui_builder_tabs.criar_aba_entrada(notebook, global_state, ui_callbacks, ui_elements, show_msg_func_ref)
    aba_programado = ui_builder_tabs.criar_aba_programado(notebook, global_state, ui_callbacks, ui_elements, show_msg_func_ref)
    aba_saida = ui_builder_tabs.criar_aba_saida(notebook, global_state, ui_callbacks, ui_elements, show_msg_func_ref)
    aba_cadastro = ui_builder_tabs.criar_aba_cadastro(notebook, global_state, ui_callbacks, ui_elements, show_msg_func_ref)
    aba_hist_entrada = ui_builder_tabs.criar_aba_historico_entrada(notebook, global_state, ui_callbacks, ui_elements, show_msg_func_ref)
    aba_hist_saida = ui_builder_tabs.criar_aba_historico_saida(notebook, global_state, ui_callbacks, ui_elements, show_msg_func_ref)
    aba_creditos = ui_builder_tabs.criar_aba_creditos(notebook, global_state, ui_callbacks, ui_elements, show_msg_func_ref)
    aba_config = ui_builder_tabs.criar_aba_configuracoes(notebook, global_state, ui_callbacks, ui_elements, show_msg_func_ref)

    notebook.add(aba_entrada, text="Entrada")
    notebook.add(aba_programado, text="Programado")
    notebook.add(aba_saida, text="Saída")
    notebook.add(aba_cadastro, text="Cadastro")
    notebook.add(aba_hist_entrada, text="Histórico de Entrada")
    notebook.add(aba_hist_saida, text="Histórico de Saída")
    notebook.add(aba_creditos, text="Créditos")
    notebook.add(aba_config, text="Configurações")

    notebook.bind("<<NotebookTabChanged>>", lambda event: ui_event_handlers.on_tab_change(event, ui_elements, global_state, ui_callbacks, show_msg_func_ref))
    
    return ui_elements

# --- Lógica de Inicialização da UI ---
def set_initial_widget_states(global_state, ui_callbacks):
    """Define os estados iniciais dos widgets após a construção da UI."""
    if not PYWIN32_AVAILABLE and sys.platform == 'win32':
        show_message_thread_safe("warning", "pywin32 Ausente", "Impressão direta e listagem de impressoras desabilitadas.")
    
    if ui_elements.get('combo_modalidade'):
        ui_elements['combo_modalidade'].current(0)
    if ui_elements.get('combo_tipo'):
        ui_elements['combo_tipo'].current(0)
    if global_state.get('ultimo_atendente_entrada') in global_state.get('lista_atendentes', []):
        ui_elements.get('combo_atendente').set(global_state['ultimo_atendente_entrada'])

    try:
        # Carrega apenas os dados que são rápidos e necessários para a primeira aba
        ui_helpers.atualizar_todas_listas_clientes(ui_elements, ui_callbacks['ler_clientes'])
        ui_helpers.atualizar_estado_botoes_impressao(ui_elements, global_state)
    except Exception as e:
        show_message_thread_safe("error", "Erro de Inicialização", f"Falha ao popular dados iniciais: {e}")

    if ui_elements.get('entry_pesquisa_remetente'):
        ui_elements['entry_pesquisa_remetente'].focus_set()