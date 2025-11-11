# ui_helpers.py
import tkinter as tk
from tkinter import ttk
import datetime

def formatar_cliente(nome, telefone):
    """Formata a exibição do cliente para comboboxes."""
    return f"{nome} - {telefone if telefone else 'N/A'}"

def popular_treeview_clientes(tree_widget, ler_clientes_func, filter_text=None):
    """Popula o Treeview de clientes com dados do banco de dados, com filtro opcional."""
    if not tree_widget or not tree_widget.winfo_exists():
        return
    for item in tree_widget.get_children():
        tree_widget.delete(item)

    clientes_data = ler_clientes_func()

    filtered_clientes = []
    if filter_text:
        filter_text_lower = filter_text.lower()
        for nome, data in clientes_data.items():
            if filter_text_lower in nome.lower() or \
               (data.get('telefone') and filter_text_lower in data['telefone']) or \
               (data.get('ncliente') and data['ncliente'] and filter_text_lower in data['ncliente']):
                filtered_clientes.append((nome, data))
    else:
        filtered_clientes = list(clientes_data.items())

    filtered_clientes.sort(key=lambda x: x[0].lower())

    for nome, data in filtered_clientes:
        telefone = data.get('telefone', '')
        ncliente = data.get('ncliente', '')
        tree_widget.insert("", "end", values=(nome, telefone, ncliente))

def popular_treeview_creditos(tree_widget, ler_creditos_func):
    """Popula o Treeview de créditos com clientes que possuem NCliente."""
    if not tree_widget or not tree_widget.winfo_exists(): return
    for item in tree_widget.get_children():
        tree_widget.delete(item)

    creditos_data = ler_creditos_func()
    for item in creditos_data:
        tree_widget.insert("", "end", values=(item['nome'], item['ncliente']))

def _ensure_combo_values_updated(entry_widget, combobox_widget, ler_clientes_func):
    """Função interna para atualizar os valores de um combobox de clientes."""
    if not entry_widget or not combobox_widget or not combobox_widget.winfo_exists():
        return

    texto_digitado = entry_widget.get().strip().lower()
    clientes_data = ler_clientes_func()

    matches = []
    if not texto_digitado:
        matches = [formatar_cliente(n, d.get('telefone')) for n, d in clientes_data.items()]
    else:
        for nome, data in clientes_data.items():
            item_formatado = formatar_cliente(nome, data.get('telefone'))
            if texto_digitado in item_formatado.lower():
                matches.append(item_formatado)

    combobox_widget['values'] = sorted(matches, key=str.lower)

def atualizar_combobox_clientes(entry_widget, combobox_widget, ler_clientes_func):
    """Gatilho para atualizar um combobox de clientes."""
    _ensure_combo_values_updated(entry_widget, combobox_widget, ler_clientes_func)

def atualizar_todas_listas_clientes(ui_elements, ler_clientes_func):
    """Atualiza todos os comboboxes e a treeview de clientes."""
    comboboxes_info = [
        ('combo_remetente', 'entry_pesquisa_remetente'),
        ('combo_destinatario', 'entry_pesquisa_destinatario'),
        ('combo_cliente_saida', 'entry_pesquisa_cliente_saida'),
        ('combo_cliente_hist_saida', 'entry_pesquisa_cliente_hist_saida'),
        ('combo_cliente_hist_entrada', 'entry_pesquisa_cliente_hist_entrada'),
        ('combo_dest_hist_entrada', 'entry_pesquisa_dest_hist_entrada'),
        ('combo_remetente_programado', 'entry_pesquisa_remetente_programado')
    ]
    for combo_name, entry_name in comboboxes_info:
        combo_w = ui_elements.get(combo_name)
        entry_w = ui_elements.get(entry_name)
        if combo_w and entry_w:
            _ensure_combo_values_updated(entry_w, combo_w, ler_clientes_func)

    tree_clientes_w = ui_elements.get('tree_clientes_cadastro')
    if tree_clientes_w:
        popular_treeview_clientes(tree_clientes_w, ler_clientes_func)

def atualizar_estado_botoes_impressao(ui_elements, global_state):
    """Atualiza o texto e o estado dos botões de impressão."""
    btn_gerar_w = ui_elements.get('botao_gerar')
    if btn_gerar_w:
        can_print_setup = global_state.get('PYWIN32_AVAILABLE') and global_state.get('selected_printer_name')
        if global_state.get('g_enable_printing') and can_print_setup:
            btn_gerar_w.config(text="Gerar Envelope e Imprimir Etiqueta")
        elif global_state.get('g_enable_printing') and not can_print_setup:
            btn_gerar_w.config(text="Gerar Envelope (Imp. Habilitada, Não Config.)")
        else:
            btn_gerar_w.config(text="Gerar Envelope (Impressão Desabilitada)")

    btn_imp_ult_w = ui_elements.get('botao_imprimir_ultima_etiqueta')
    if btn_imp_ult_w:
        can_reprint = all([
            global_state.get('PYWIN32_AVAILABLE'),
            global_state.get('selected_printer_name'),
            global_state.get('ultima_etiqueta_codigo'),
            global_state.get('g_enable_printing')
        ])
        btn_imp_ult_w.config(state=tk.NORMAL if can_reprint else tk.DISABLED)

def update_title_from_config(janela_ref, app_title_base, app_title_local, app_by_line):
    """Atualiza o título da janela principal."""
    window_title = f"{app_title_base}{' - ' + app_title_local if app_title_local and app_title_local.strip() else ''} {app_by_line}"
    janela_ref.title(window_title)

def popular_combo_impressoras(ui_elements, global_state, listar_impressoras_windows_func):
    """Popula o combobox de impressoras na aba de configurações."""
    combo_cfg_printer_w = ui_elements.get('combo_cfg_printer')
    # Adicionado para evitar erro se PYWIN32_AVAILABLE for None
    pywin32_available = global_state.get('PYWIN32_AVAILABLE', False)
    if combo_cfg_printer_w:
        printers_list = listar_impressoras_windows_func() if pywin32_available else ["pywin32 não instalado"]
        combo_cfg_printer_w['values'] = printers_list
        selected_printer = global_state.get('selected_printer_name')
        if selected_printer in printers_list:
            combo_cfg_printer_w.set(selected_printer)
        elif not pywin32_available:
            combo_cfg_printer_w.set("pywin32 não instalado")
        else:
            combo_cfg_printer_w.set('') # Limpa se a impressora salva não existe mais


def exibir_historico(tree_widget, tipo_historico, ui_callbacks, ui_elements, **filters): # Adicionado ui_elements
    """Exibe o histórico de entradas ou saídas em uma Treeview e atualiza a contagem."""
    if not tree_widget or not tree_widget.winfo_exists(): return

    for item in tree_widget.get_children():
        tree_widget.delete(item)

    historico_data = []
    keys_order = []

    if tipo_historico == 'entradas':
        historico_data = ui_callbacks['ler_historico_entradas_db'](**filters)
        keys_order = ['data_hora_registro', 'codigo', 'remetente_nome', 'remetente_telefone',
                      'destinatario_nome', 'destinatario_telefone', 'modalidade',
                      'atendente_registro', 'tipo_pacote']
    elif tipo_historico == 'saidas':
        historico_data = ui_callbacks['ler_historico_saidas_db'](**filters)
        keys_order = ['data_hora_saida', 'codigo_envelope', 'destinatario_nome',
                      'destinatario_telefone', 'remetente_nome',
                      'data_hora_registro_original', 'atendente_registro_original', 'atendente_saida']
    else:
        return

    # Popula a Treeview
    for envio_dict in historico_data:
        values = []
        for key in keys_order:
            val = envio_dict.get(key, '')
            if isinstance(val, datetime.datetime):
                values.append(val.strftime("%d/%m/%y %H:%M"))
            else:
                values.append(val)
        tree_widget.insert("", "end", values=tuple(values))

    # --- Atualização da Contagem ---
    # Atualiza apenas se for o histórico de entradas
    if tipo_historico == 'entradas':
        contagem = len(tree_widget.get_children())
        # Tenta obter a StringVar do ui_elements
        strvar_contagem = ui_elements.get('strvar_contagem_hist_entrada')
        if strvar_contagem:
            # Atualiza o texto da StringVar
            texto_contagem = f"Exibindo: {contagem} envelope{'s' if contagem != 1 else ''}"
            strvar_contagem.set(texto_contagem)

def atualizar_display_config_aba(ui_elements, global_state):
    """Atualiza os widgets na aba de configurações com os valores atuais."""
    frame_db_info_w = ui_elements.get('frame_config_db_info')
    if frame_db_info_w:
        for widget in frame_db_info_w.winfo_children():
            widget.destroy()

        db_config = global_state.get('db_mysql_config', {})
        db_info_text = (f"Host: {db_config.get('host', 'N/D')}\n"
                        f"Porta: {db_config.get('port', 'N/D')}\n"
                        f"Usuário: {db_config.get('user', 'N/D')}\n"
                        f"Banco de Dados: {db_config.get('database', 'N/D')}")
        ttk.Label(frame_db_info_w, text=db_info_text, justify=tk.LEFT).pack(anchor="w", padx=5, pady=5)

        # Tenta importar dinamicamente para evitar dependência circular completa
        try:
            from config_manager import CONFIG_FILE_NAME
            ttk.Label(frame_db_info_w, text=f"Para alterar, edite: {CONFIG_FILE_NAME}", style="Note.TLabel").pack(anchor="w", padx=5, pady=(0,5))
        except ImportError:
             ttk.Label(frame_db_info_w, text="Para alterar, edite o arquivo de configuração.", style="Note.TLabel").pack(anchor="w", padx=5, pady=(0,5))


    ui_elements['strvar_selected_printer'].set(global_state.get('selected_printer_name', ''))
    ui_elements['boolvar_enable_printing'].set(global_state.get('g_enable_printing', True))
    ui_elements['strvar_font_dest'].set(str(global_state.get('g_font_size_dest_pts', 7)))
    ui_elements['strvar_font_code'].set(str(global_state.get('g_font_size_code_pts', 20)))
    ui_elements['strvar_font_data'].set(str(global_state.get('g_font_size_data_pts', 10)))
    ui_elements['strvar_line_spacing'].set(str(global_state.get('g_line_spacing_mm', 1.0)))