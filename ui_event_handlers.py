# ui_event_handlers.py
import tkinter as tk
from tkinter import ttk
import threading
import datetime
import traceback
import webbrowser

# Importar helpers para manter a lógica de UI separada
import ui_helpers

def handle_dynamic_client_search(event, entry_widget, combobox_widget, ler_clientes_func):
    """
    Filtra a lista de um combobox de clientes e atualiza o texto para o primeiro resultado.
    """
    texto_digitado = entry_widget.get().strip().lower()
    clientes_data = ler_clientes_func()

    matches = []
    if not texto_digitado:
        matches = [ui_helpers.formatar_cliente(n, d.get('telefone')) for n, d in clientes_data.items()]
    else:
        for nome, data in clientes_data.items():
            item_formatado = ui_helpers.formatar_cliente(nome, data.get('telefone'))
            if texto_digitado in item_formatado.lower():
                matches.append(item_formatado)

    sorted_matches = sorted(matches, key=str.lower)
    combobox_widget['values'] = sorted_matches

    if texto_digitado and sorted_matches:
        combobox_widget.set(sorted_matches[0])
    elif not texto_digitado:
        combobox_widget.set('')

# CORREÇÃO: Adicionado o parâmetro show_message_func
def on_tab_change(event, ui_elements, global_state, ui_callbacks, show_message_func):
    """Lida com a mudança de abas no notebook principal."""
    try:
        notebook = event.widget
        if not notebook.winfo_exists(): return
        selected_tab_text = notebook.tab(notebook.select(), "text")

        if selected_tab_text == 'Cadastro':
            ui_helpers.popular_treeview_clientes(ui_elements.get('tree_clientes_cadastro'), ui_callbacks['ler_clientes'])
            if ui_elements.get('entry_nome_cadastro'): # Check if widget exists
                ui_elements['entry_nome_cadastro'].focus_set()
        elif selected_tab_text == 'Créditos':
            ui_helpers.popular_treeview_creditos(ui_elements.get('tree_creditos'), ui_callbacks['ler_creditos_db'])
            if ui_elements.get('entry_ncliente_creditos'): # Check if widget exists
                ui_elements['entry_ncliente_creditos'].focus_set()
        elif selected_tab_text == 'Saída':
            if ui_elements.get('entry_pesquisa_cliente_saida'): # Check if widget exists
                ui_elements['entry_pesquisa_cliente_saida'].focus_set()
        elif selected_tab_text == 'Entrada':
            if ui_elements.get('entry_pesquisa_remetente'): # Check if widget exists
                ui_elements['entry_pesquisa_remetente'].focus_set()
        elif selected_tab_text == 'Programado':
            frame = ui_elements.get('scrollable_frame_prog')
            if frame:
                # Limpa o frame apenas se ele já tiver sido populado antes
                if frame.winfo_children():
                    for widget in frame.winfo_children():
                        widget.destroy()
            if ui_elements.get('entry_pesquisa_remetente_programado'): # Check if widget exists
                ui_elements['entry_pesquisa_remetente_programado'].focus_set()
        elif selected_tab_text == 'Histórico de Entrada':
            resetar_filtros_hist_entrada(ui_elements, ui_callbacks)
        elif selected_tab_text == 'Histórico de Saída':
            resetar_filtro_cliente_hist_saida(ui_elements, ui_callbacks)
        elif selected_tab_text == 'Configurações':
            ui_helpers.atualizar_display_config_aba(ui_elements, global_state)
            if global_state.get('PYWIN32_AVAILABLE'):
                ui_helpers.popular_combo_impressoras(ui_elements, global_state, ui_callbacks['listar_impressoras_windows'])

    except Exception as e:
        # Usar a função show_message_func recebida como parâmetro
        show_message_func("error", "Erro Tab Change", f"Erro ao mudar de aba: {e}\n{traceback.format_exc()}")
        # Fallback para print caso show_message_func falhe ou não esteja disponível
        # print(f"Erro ao mudar de aba: {e}\n{traceback.format_exc()}")


# --- Handlers da Aba "Entrada" ---

def gerar_envelope(ui_elements, global_state, ui_callbacks, show_message_func):
    """Lógica de geração de envelope, impressão e notificação via bot."""
    # ... (código existente da função) ...
    remetente_fmt = ui_elements['combo_remetente'].get()
    destinatario_fmt = ui_elements['combo_destinatario'].get()
    modalidade = ui_elements['combo_modalidade'].get()
    atendente_selecionado = ui_elements['combo_atendente'].get()
    tipo_pacote = ui_elements['combo_tipo'].get()

    if not all([remetente_fmt, destinatario_fmt, modalidade, atendente_selecionado, tipo_pacote]):
        show_message_func("error", "Erro", "Preencha todos os campos.")
        return

    global_state['ultimo_atendente_entrada'] = atendente_selecionado
    clientes_db_raw = ui_callbacks['ler_clientes']()
    clientes_db = {nome: data for nome, data in clientes_db_raw.items()}

    rem_nome = remetente_fmt.split(' - ')[0].strip()
    rem_tel = clientes_db.get(rem_nome, {}).get('telefone')
    dest_nome = destinatario_fmt.split(' - ')[0].strip()
    dest_tel = clientes_db.get(dest_nome, {}).get('telefone')

    codigo = ui_callbacks['gerar_codigo'](dest_nome)
    data_hora_obj_reg = datetime.datetime.now()
    data_hora_reg_str = data_hora_obj_reg.strftime("%Y-%m-%d %H:%M:%S")

    dados_envio = {
        'data_hora_registro': data_hora_reg_str, 'codigo': codigo,
        'remetente_nome': rem_nome, 'remetente_telefone': rem_tel,
        'destinatario_nome': dest_nome, 'destinatario_telefone': dest_tel,
        'modalidade': modalidade, 'atendente_registro': atendente_selecionado,
        'tipo_pacote': tipo_pacote
    }

    if not ui_callbacks['salvar_nova_entrada_db'](dados_envio): return
    # Atualiza o histórico de entrada após salvar com sucesso
    resetar_filtros_hist_entrada(ui_elements, ui_callbacks)

    if global_state.get('g_enable_printing'):
        if global_state.get('PYWIN32_AVAILABLE') and global_state.get('selected_printer_name'):
            threading.Thread(target=ui_callbacks['imprimir_etiqueta_direto_windows'],
                             args=(global_state['selected_printer_name'], dest_nome, codigo, data_hora_obj_reg,
                                   global_state['g_font_size_dest_pts'], global_state['g_font_size_code_pts'],
                                   global_state['g_font_size_data_pts'], global_state['g_line_spacing_mm']), daemon=True).start()

    if dest_tel and dest_tel != "N/A":
        evento_bot = {
            "tipo_evento": "novo_envelope", "codigo": codigo,
            "destinatario_telefone": dest_tel, "destinatario_nome": dest_nome,
            "remetente_nome": rem_nome, "remetente_telefone": rem_tel,
            "tipo_pacote": tipo_pacote, "data_hora_registro": data_hora_reg_str,
            "atendente_registro": atendente_selecionado,
            "nome_local": global_state.get('app_title_local', 'nossa loja')
        }
        threading.Thread(target=ui_callbacks['enviar_notificacao_via_bot'], args=(evento_bot,), daemon=True).start()

    global_state.update({
        'ultima_etiqueta_destinatario_nome': dest_nome,
        'ultima_etiqueta_codigo': codigo,
        'ultima_etiqueta_data_hora': data_hora_reg_str
    })
    ui_helpers.atualizar_estado_botoes_impressao(ui_elements, global_state)

    ui_elements['combo_destinatario'].set('')
    ui_elements['entry_pesquisa_destinatario'].delete(0, tk.END)
    ui_elements['entry_pesquisa_destinatario'].focus_set()


def imprimir_ultima_etiqueta(global_state, ui_callbacks, show_message_func):
    """Reimprime a última etiqueta gerada."""
    # ... (código existente da função) ...
    if not global_state.get('g_enable_printing'):
        show_message_func("info", "Impressão Desabilitada", "Impressão desabilitada nas configurações.")
        return
    if global_state.get('ultima_etiqueta_codigo'):
        if not global_state.get('selected_printer_name') and global_state.get('PYWIN32_AVAILABLE'):
            show_message_func("warning", "Impressora Não Configurada", "Nenhuma impressora configurada.")
            return
        try:
            data_hora_obj = datetime.datetime.strptime(global_state['ultima_etiqueta_data_hora'], "%Y-%m-%d %H:%M:%S")
            threading.Thread(target=ui_callbacks['imprimir_etiqueta_direto_windows'],
                             args=(global_state['selected_printer_name'],
                                   global_state['ultima_etiqueta_destinatario_nome'],
                                   global_state['ultima_etiqueta_codigo'],
                                   data_hora_obj,
                                   global_state['g_font_size_dest_pts'],
                                   global_state['g_font_size_code_pts'],
                                   global_state['g_font_size_data_pts'],
                                   global_state['g_line_spacing_mm']), daemon=True).start()
        except Exception as e:
            show_message_func("error", "Erro Reimprimir", f"Falha ao reimprimir: {e}")
    else:
        show_message_func("info", "Aviso", "Nenhuma etiqueta recente para reimprimir.")


# --- Handlers da Aba "Programado" ---

def refresh_programados_e_invalidar_cache(ui_elements, global_state, ui_callbacks, show_message_func):
    """
    Invalida o cache de clientes e em seguida chama a função para buscar os
    envelopes programados, garantindo que os dados sejam os mais recentes.
    """
    # ... (código existente da função) ...
    # Passo 1: Invalida o cache de clientes.
    ui_callbacks['invalidar_cache_clientes']()
    print("[CACHE] Cache de clientes invalidado manualmente pelo botão Atualizar.")
    # Passo 2: Chama a função de busca original.
    buscar_programados_ui(ui_elements, global_state, ui_callbacks, show_message_func)


def buscar_programados_ui(ui_elements, global_state, ui_callbacks, show_message_func):
    """Busca e exibe os envelopes programados usando um layout de grade."""
    # ... (código existente da função) ...
    frame_lista = ui_elements.get('scrollable_frame_prog')
    combo_rem_w = ui_elements.get('combo_remetente_programado')
    if not frame_lista or not combo_rem_w: return

    for widget in frame_lista.winfo_children():
        widget.destroy()

    remetente_selecionado_fmt = combo_rem_w.get()
    if not remetente_selecionado_fmt:
        show_message_func("error", "Erro", "Selecione um remetente para buscar.")
        return

    try:
        rem_telefone = remetente_selecionado_fmt.split(' - ')[1].strip()
    except IndexError:
        show_message_func("error", "Erro", "Formato do cliente inválido.")
        return

    programados = ui_callbacks['ler_programados_por_remetente'](rem_telefone)
    if not programados:
        ttk.Label(frame_lista, text="Nenhum envelope programado encontrado para este remetente.").pack(pady=10)
        return

    for i, prog_data in enumerate(programados):
        row_frame = ttk.Frame(frame_lista, padding=5, relief="solid", borderwidth=1)
        row_frame.pack(fill='x', expand=True, pady=5, padx=5)
        row_frame.grid_columnconfigure(0, weight=3)
        row_frame.grid_columnconfigure(2, weight=1)
        row_frame.grid_columnconfigure(4, weight=1)
        row_frame.grid_columnconfigure(5, weight=0)

        data_hora_val = prog_data.get('data_hora_programado')
        data_hora_obj = None
        if isinstance(data_hora_val, str):
            try:
                data_hora_obj = datetime.datetime.strptime(data_hora_val, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                data_hora_obj = datetime.datetime.now()
        elif isinstance(data_hora_val, datetime.datetime):
            data_hora_obj = data_hora_val
        else:
            data_hora_obj = datetime.datetime.now()
        data_hora_str = data_hora_obj.strftime("%d/%m/%y às %H:%M")

        dest_nome = prog_data.get('destinatario_nome', 'N/D')
        info_text = f"{data_hora_str} - Para: {dest_nome}"
        ttk.Label(row_frame, text=info_text, anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ttk.Label(row_frame, text="Modalidade:").grid(row=0, column=1, padx=(10, 2), pady=5, sticky="w")
        modalidades_programado = ["Só entregar", "Receber"]
        combo_modalidade = ttk.Combobox(row_frame, values=modalidades_programado, width=15, state="readonly")
        combo_modalidade.set(modalidades_programado[0])
        combo_modalidade.grid(row=0, column=2, padx=2, pady=5, sticky="ew")

        ttk.Label(row_frame, text="Pacote:").grid(row=0, column=3, padx=(10, 2), pady=5, sticky="w")
        combo_pacote = ttk.Combobox(row_frame, values=global_state['lista_tipos_pacote'], width=15)
        if global_state['lista_tipos_pacote']:
            combo_pacote.current(0)
        combo_pacote.grid(row=0, column=4, padx=2, pady=5, sticky="ew")

        btn_gerar = ttk.Button(row_frame, text="Gerar Envelope", style="Primary.TButton",
                               command=lambda p=prog_data, m=combo_modalidade, c=combo_pacote: gerar_envelope_programado_linha(p, m, c, ui_elements, global_state, ui_callbacks, show_message_func))
        btn_gerar.grid(row=0, column=5, padx=(10, 5), pady=5)



def gerar_envelope_programado_linha(prog_data, combo_modalidade_widget, combo_pacote_widget, ui_elements, global_state, ui_callbacks, show_message_func):
    """Gera um envelope a partir de uma linha específica da lista de programados."""
    # ... (código existente da função) ...
    combo_rem_w = ui_elements.get('combo_remetente_programado')
    combo_atendente_w = ui_elements.get('combo_atendente_prog')

    remetente_fmt = combo_rem_w.get()
    modalidade = combo_modalidade_widget.get()
    tipo_pacote = combo_pacote_widget.get()
    atendente_selecionado = combo_atendente_w.get()

    if not all([modalidade, tipo_pacote, atendente_selecionado]):
        show_message_func("error", "Erro", "Selecione a Modalidade, o Pacote e o Atendente.")
        return

    id_programado = prog_data['id']
    dest_nome = prog_data['destinatario_nome']
    dest_tel = prog_data['destinatario_telefone']
    rem_nome, rem_tel = remetente_fmt.split(' - ')[0].strip(), remetente_fmt.split(' - ')[1].strip()

    codigo = ui_callbacks['gerar_codigo'](dest_nome)
    data_hora_obj_reg = datetime.datetime.now()
    data_hora_reg_str = data_hora_obj_reg.strftime("%Y-%m-%d %H:%M:%S")

    dados_envio = {
        'data_hora_registro': data_hora_reg_str, 'codigo': codigo,
        'remetente_nome': rem_nome, 'remetente_telefone': rem_tel,
        'destinatario_nome': dest_nome, 'destinatario_telefone': dest_tel,
        'modalidade': modalidade,
        'atendente_registro': atendente_selecionado,
        'tipo_pacote': tipo_pacote
    }

    if not ui_callbacks['processar_envelope_programado'](dados_envio, id_programado):
        buscar_programados_ui(ui_elements, global_state, ui_callbacks, show_message_func)
        return

    resetar_filtros_hist_entrada(ui_elements, ui_callbacks)

    if global_state.get('g_enable_printing'):
        if global_state.get('PYWIN32_AVAILABLE') and global_state.get('selected_printer_name'):
            threading.Thread(target=ui_callbacks['imprimir_etiqueta_direto_windows'],
                             args=(global_state['selected_printer_name'], dest_nome, codigo, data_hora_obj_reg,
                                   global_state['g_font_size_dest_pts'], global_state['g_font_size_code_pts'],
                                   global_state['g_font_size_data_pts'], global_state['g_line_spacing_mm']), daemon=True).start()

    if dest_tel and dest_tel != "N/A":
        evento_bot = {
            "tipo_evento": "novo_envelope", "codigo": codigo,
            "destinatario_telefone": dest_tel, "destinatario_nome": dest_nome,
            "remetente_nome": rem_nome, "remetente_telefone": rem_tel,
            "tipo_pacote": tipo_pacote, "data_hora_registro": data_hora_reg_str,
            "atendente_registro": atendente_selecionado,
            "nome_local": global_state.get('app_title_local', 'nossa loja')
        }
        threading.Thread(target=ui_callbacks['enviar_notificacao_via_bot'], args=(evento_bot,), daemon=True).start()

    show_message_func("info", "Sucesso", f"Envelope {codigo} gerado com sucesso para {dest_nome}.")
    buscar_programados_ui(ui_elements, global_state, ui_callbacks, show_message_func)



# --- Handlers da Aba "Saída" ---

def buscar_envelopes_para_saida(ui_elements, global_state, ui_callbacks, show_message_func):
    """Callback para buscar envelopes pendentes na aba de saída."""
    # ... (código existente da função) ...
    cs_w = ui_elements.get('combo_cliente_saida')
    ts_w = ui_elements.get('tree_saida')
    if not cs_w or not ts_w: return

    cli_sel_completo = cs_w.get()
    if not cli_sel_completo:
        show_message_func("error", "Erro Busca Saída", "Selecione um cliente destinatário.")
        return
    nome_dest_busca = cli_sel_completo.split(' - ')[0].strip()
    envios_pendentes = ui_callbacks['buscar_envelopes_para_saida'](nome_dest_busca, show_message_func)

    for item in ts_w.get_children(): ts_w.delete(item)
    global_state['envios_exibidos_na_saida'] = envios_pendentes

    if not envios_pendentes:
        show_message_func("info", "Info", f"Nenhum envelope pendente encontrado para '{nome_dest_busca}'.")
        return

    for env_d in envios_pendentes:
        dr_val = env_d.get('data_hora_registro')
        dr_str_fmt = dr_val.strftime("%d/%m/%y %H:%M") if isinstance(dr_val, datetime.datetime) else str(dr_val)
        ts_w.insert("", "end", values=(
            "[ ]", env_d.get('codigo', ''), dr_str_fmt,
            env_d.get('remetente_nome', ''), env_d.get('destinatario_nome', ''),
            env_d.get('modalidade', ''), env_d.get('atendente_registro', ''),
            env_d.get('tipo_pacote', '')
        ))


def dar_baixa_envelopes(ui_elements, global_state, ui_callbacks, show_message_func):
    """Lida com a lógica de dar baixa nos envelopes selecionados."""
    # ... (código existente da função) ...
    ts_w = ui_elements.get('tree_saida')
    cas_w = ui_elements.get('combo_atendente_saida')
    if not ts_w or not cas_w: return

    atendente_da_saida = cas_w.get()
    if not atendente_da_saida:
        show_message_func("error", "Erro Baixa", "Selecione o 'Atendente da Saída'.")
        return

    codigos_para_baixa = [ts_w.item(item_id, 'values')[1] for item_id in ts_w.get_children() if ts_w.item(item_id, 'values')[0] == "[x]"]
    if not codigos_para_baixa:
        show_message_func("error", "Erro Baixa", "Nenhum envelope selecionado para baixa.")
        return

    data_hora_despacho_obj = datetime.datetime.now()
    data_hora_despacho_iso = data_hora_despacho_obj.strftime("%Y-%m-%d %H:%M:%S")

    cliente_para_msg = ui_elements.get('combo_cliente_saida').get().split(' - ')[0].strip()
    if not show_message_func("askyesno", "Confirmar Baixa", f"Dar baixa em {len(codigos_para_baixa)} envelope(s) para '{cliente_para_msg}'?"):
        return

    sucessos = 0
    envelopes_baixados_info = []
    destinatario_telefone_final = None

    for codigo in codigos_para_baixa:
        envio_original = next((env for env in global_state.get('envios_exibidos_na_saida', []) if env.get('codigo') == codigo), None)
        if not envio_original: continue

        data_hora_reg_orig_val = envio_original.get('data_hora_registro')
        data_hora_reg_orig_str = data_hora_reg_orig_val.strftime("%Y-%m-%d %H:%M:%S") if isinstance(data_hora_reg_orig_val, datetime.datetime) else str(data_hora_reg_orig_val)

        dados_saida = {
            **envio_original,
            'codigo_envelope': envio_original.get('codigo'),
            'data_hora_registro_original': data_hora_reg_orig_str,
            'atendente_registro_original': envio_original.get('atendente_registro'),
            'data_hora_saida': data_hora_despacho_iso,
            'atendente_saida': atendente_da_saida
        }

        if ui_callbacks['salvar_saida_db'](dados_saida):
            sucessos += 1
            envelopes_baixados_info.append(dados_saida)
            if not destinatario_telefone_final:
                destinatario_telefone_final = dados_saida.get('destinatario_telefone')

    if sucessos > 0:
        resetar_filtro_cliente_hist_saida(ui_elements, ui_callbacks)
        if destinatario_telefone_final and destinatario_telefone_final != "N/A":
            evento_bot = {
                "tipo_evento": "baixa_multiplos_envelopes",
                "destinatario_telefone": destinatario_telefone_final,
                "destinatario_nome": cliente_para_msg,
                "data_hora_saida": data_hora_despacho_iso,
                "envelopes": envelopes_baixados_info
            }
            threading.Thread(target=ui_callbacks['enviar_notificacao_via_bot'], args=(evento_bot,), daemon=True).start()

    show_message_func("info", "Baixa Concluída", f"{sucessos} envelope(s) baixado(s) com sucesso.")
    buscar_envelopes_para_saida(ui_elements, global_state, ui_callbacks, show_message_func)


def toggle_checkbox_saida(event):
    """Marca/desmarca o checkbox na treeview de saída."""
    # ... (código existente da função) ...
    tv = event.widget
    item_id = tv.identify_row(event.y)
    col_id_str = tv.identify_column(event.x)
    if not item_id or col_id_str != '#1': return
    current_values = list(tv.item(item_id, 'values'))
    current_values[0] = "[x]" if current_values[0] == "[ ]" else "[ ]"
    tv.item(item_id, values=tuple(current_values))


# --- Handlers da Aba "Cadastro" ---

def salvar_cliente(ui_elements, ui_callbacks, show_message_func):
    """Salva um novo cliente ou atualiza um existente."""
    # ... (código existente da função) ...
    nome = ui_elements['entry_nome_cadastro'].get()
    telefone = ui_elements['entry_telefone_cadastro'].get()
    ncliente = ui_elements['entry_ncliente_cadastro'].get()

    if ui_callbacks['salvar_cliente'](nome, telefone, ncliente or None):
        ui_elements['entry_nome_cadastro'].delete(0, tk.END)
        ui_elements['entry_telefone_cadastro'].delete(0, tk.END)
        ui_elements['entry_ncliente_cadastro'].delete(0, tk.END)
        ui_elements['entry_nome_cadastro'].focus_set()
        ui_helpers.atualizar_todas_listas_clientes(ui_elements, ui_callbacks['ler_clientes'])
        ui_helpers.popular_treeview_creditos(ui_elements.get('tree_creditos'), ui_callbacks['ler_creditos_db'])


def selecionar_cliente_para_edicao(event, ui_elements):
    """Preenche os campos de cadastro ao selecionar na treeview."""
    # ... (código existente da função) ...
    tree = event.widget
    selected_items = tree.selection()
    if not selected_items: return
    values = tree.item(selected_items[0], 'values')
    if values and len(values) >= 3:
        ui_elements['entry_nome_cadastro'].delete(0, tk.END); ui_elements['entry_nome_cadastro'].insert(0, values[0])
        ui_elements['entry_telefone_cadastro'].delete(0, tk.END); ui_elements['entry_telefone_cadastro'].insert(0, values[1])
        ui_elements['entry_ncliente_cadastro'].delete(0, tk.END); ui_elements['entry_ncliente_cadastro'].insert(0, values[2] if values[2] else "")
        ui_elements['entry_nome_cadastro'].focus_set()


def filtrar_clientes_cadastro(event, ui_elements, ui_callbacks):
    """Filtra a treeview de clientes na aba de cadastro."""
    # ... (código existente da função) ...
    filter_text = ui_elements['entry_pesquisa_cliente_cadastro_tree'].get()
    ui_helpers.popular_treeview_clientes(ui_elements.get('tree_clientes_cadastro'), ui_callbacks['ler_clientes'], filter_text)


# --- Handlers da Aba "Créditos" ---
def abrir_url_credito(ui_elements, action, show_message_func):
    """Abre a URL para adicionar ou remover créditos."""
    # ... (código existente da função) ...
    ncliente = ui_elements['entry_ncliente_creditos'].get().strip()
    if not ncliente:
        show_message_func("error", "Erro", "Digite um NCliente.")
        return

    base_url = "https://www.dominariacg.com.br/?view=ecom/admin/"
    url_map = {
        'add': f"{base_url}creditoadd&user={ncliente}",
        'remove': f"{base_url}creditodel&user={ncliente}"
    }

    try:
        webbrowser.open(url_map[action])
        ui_elements['entry_ncliente_creditos'].delete(0, tk.END)
    except Exception as e:
        show_message_func("error", "Erro URL", f"Falha ao abrir URL: {e}")


def selecionar_credito_para_edicao(event, ui_elements):
    """Preenche o campo NCliente ao selecionar na treeview de créditos."""
    # ... (código existente da função) ...
    tree = event.widget
    selected_items = tree.selection()
    if not selected_items: return
    values = tree.item(selected_items[0], 'values')
    if values and len(values) >= 2:
        ui_elements['entry_ncliente_creditos'].delete(0, tk.END)
        ui_elements['entry_ncliente_creditos'].insert(0, values[1])
        ui_elements['entry_ncliente_creditos'].focus_set()


# --- Handlers das Abas de "Histórico" ---
def aplicar_filtros_hist_entrada(ui_elements, ui_callbacks):
    """Aplica os filtros selecionados na aba de histórico de entrada."""
    # ... (código existente da função) ...
    start_date_str = ui_elements.get('entry_data_inicial_hist').get()
    end_date_str = ui_elements.get('entry_data_final_hist').get()
    rem_filter_nome = ui_elements.get('combo_cliente_hist_entrada').get().split(' - ')[0].strip() if ui_elements.get('combo_cliente_hist_entrada').get() else ''
    dest_filter_nome = ui_elements.get('combo_dest_hist_entrada').get().split(' - ')[0].strip() if ui_elements.get('combo_dest_hist_entrada').get() else ''

    user_filter_active = bool(start_date_str or end_date_str or rem_filter_nome or dest_filter_nome)

    start_date_query = None
    end_date_query = None

    if user_filter_active:
        if start_date_str:
            start_date_query = ui_callbacks['parse_user_date'](start_date_str)
            if start_date_query is None and start_date_str: return
        if end_date_str:
            end_date_query = ui_callbacks['parse_user_date'](end_date_str)
            if end_date_query is None and end_date_str: return
    else:
        end_date_query = datetime.datetime.now()
        start_date_query = end_date_query - datetime.timedelta(days=30)

    ui_helpers.exibir_historico(ui_elements.get('tree_historico'), 'entradas', ui_callbacks, ui_elements,
                     filter_start_date=start_date_query,
                     filter_end_date=end_date_query,
                     filter_remetente_nome=rem_filter_nome if rem_filter_nome else None,
                     filter_destinatario_nome=dest_filter_nome if dest_filter_nome else None)


def resetar_filtros_hist_entrada(ui_elements, ui_callbacks):
    """Limpa os filtros e recarrega o histórico de entrada com o padrão de 30 dias."""
    # ... (código existente da função) ...
    for name in ['entry_data_inicial_hist', 'entry_data_final_hist', 'entry_pesquisa_cliente_hist_entrada', 'entry_pesquisa_dest_hist_entrada']:
        if ui_elements.get(name): ui_elements.get(name).delete(0, tk.END)
    for name in ['combo_cliente_hist_entrada', 'combo_dest_hist_entrada']:
        if ui_elements.get(name): ui_elements.get(name).set('')
    aplicar_filtros_hist_entrada(ui_elements, ui_callbacks)


def aplicar_filtro_cliente_hist_saida(ui_elements, ui_callbacks):
    """Aplica o filtro de cliente no histórico de saída."""
    # ... (código existente da função) ...
    cli_filter_nome = ui_elements.get('combo_cliente_hist_saida').get().split(' - ')[0].strip() if ui_elements.get('combo_cliente_hist_saida').get() else ''

    user_filter_active = bool(cli_filter_nome)

    start_date_query = None
    end_date_query = None

    if not user_filter_active:
        end_date_query = datetime.datetime.now()
        start_date_query = end_date_query - datetime.timedelta(days=30)

    ui_helpers.exibir_historico(ui_elements.get('tree_historico_saida'), 'saidas', ui_callbacks, ui_elements,
                                filter_destinatario_nome=cli_filter_nome if cli_filter_nome else None,
                                filter_start_date=start_date_query,
                                filter_end_date=end_date_query)


def resetar_filtro_cliente_hist_saida(ui_elements, ui_callbacks):
    """Limpa o filtro e recarrega o histórico de saída com o padrão de 30 dias."""
    # ... (código existente da função) ...
    if ui_elements.get('entry_pesquisa_cliente_hist_saida'):
        ui_elements.get('entry_pesquisa_cliente_hist_saida').delete(0, tk.END)
    if ui_elements.get('combo_cliente_hist_saida'):
        ui_elements.get('combo_cliente_hist_saida').set('')
    aplicar_filtro_cliente_hist_saida(ui_elements, ui_callbacks)


# --- Handlers da Aba "Configurações" ---
def salvar_configuracoes(ui_elements, global_state, ui_callbacks, show_message_func):
    """Salva todas as configurações da aba de configurações."""
    # ... (código existente da função) ...
    try:
        global_state['selected_printer_name'] = ui_elements['strvar_selected_printer'].get()
        global_state['g_enable_printing'] = ui_elements['boolvar_enable_printing'].get()
        global_state['g_font_size_dest_pts'] = int(ui_elements['strvar_font_dest'].get())
        global_state['g_font_size_code_pts'] = int(ui_elements['strvar_font_code'].get())
        global_state['g_font_size_data_pts'] = int(ui_elements['strvar_font_data'].get())
        global_state['g_line_spacing_mm'] = float(ui_elements['strvar_line_spacing'].get().replace(",", "."))

        if ui_callbacks['salvar_configuracoes_atuais_para_arquivo'](global_state, global_state['COLOR_CONFIG_MAP']):
            show_message_func("info", "Configurações Salvas", "Configurações salvas com sucesso.")
            ui_helpers.atualizar_estado_botoes_impressao(ui_elements, global_state)
        else:
            show_message_func("error", "Erro ao Salvar", "Falha ao salvar o arquivo de configurações.")
    except (ValueError, TypeError) as e:
        show_message_func("error", "Valores Inválidos", f"Verifique os valores numéricos nas configurações. Erro: {e}")