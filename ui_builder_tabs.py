# ui_builder_tabs.py
import tkinter as tk
from tkinter import ttk

# Importa os outros módulos de UI para definir os callbacks dos widgets
import ui_helpers
import ui_event_handlers

def criar_aba_entrada(notebook, global_state, ui_callbacks, ui_elements, show_message_func):
    """Cria e retorna a aba 'Entrada'."""
    aba = ttk.Frame(notebook, padding="20", style="Content.TFrame")

    # --- Widgets ---
    ttk.Label(aba, text="Remetente:").grid(row=0, column=0, padx=10, pady=8, sticky="w")
    combo_remetente = ttk.Combobox(aba, width=35, state="readonly", font=('Segoe UI', 9))
    entry_pesquisa_remetente = ttk.Entry(aba, width=25, font=('Segoe UI', 9))

    ttk.Label(aba, text="Destinatário:").grid(row=1, column=0, padx=10, pady=8, sticky="w")
    combo_destinatario = ttk.Combobox(aba, width=35, state="readonly", font=('Segoe UI', 9))
    entry_pesquisa_destinatario = ttk.Entry(aba, width=25, font=('Segoe UI', 9))

    ttk.Label(aba, text="Modalidade:").grid(row=2, column=0, padx=10, pady=8, sticky="w")
    combo_modalidade = ttk.Combobox(aba, values=global_state['lista_modalidades'], state="readonly", font=('Segoe UI', 9))

    ttk.Label(aba, text="Atendente Registro:").grid(row=3, column=0, padx=10, pady=8, sticky="w")
    combo_atendente = ttk.Combobox(aba, values=global_state['lista_atendentes'], state="readonly", font=('Segoe UI', 9))

    ttk.Label(aba, text="Tipo de Pacote:").grid(row=4, column=0, padx=10, pady=8, sticky="w")
    combo_tipo = ttk.Combobox(aba, values=global_state['lista_tipos_pacote'], state="readonly", font=('Segoe UI', 9))

    botao_gerar = ttk.Button(aba, text="Gerar Envelope", style="Primary.TButton")
    botao_imprimir_ultima_etiqueta = ttk.Button(aba, text="Reimprimir Última Etiqueta", state=tk.DISABLED, style="Secondary.TButton")

    # --- Layout (Grid) ---
    combo_remetente.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
    entry_pesquisa_remetente.grid(row=0, column=2, padx=(0,10), pady=8, sticky="ew")
    combo_destinatario.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
    entry_pesquisa_destinatario.grid(row=1, column=2, padx=(0,10), pady=8, sticky="ew")
    combo_modalidade.grid(row=2, column=1, padx=5, pady=8, sticky="ew", columnspan=2)
    combo_atendente.grid(row=3, column=1, padx=5, pady=8, sticky="ew", columnspan=2)
    combo_tipo.grid(row=4, column=1, padx=5, pady=8, sticky="ew", columnspan=2)
    botao_gerar.grid(row=5, column=0, columnspan=3, padx=10, pady=(25,10), sticky="ew", ipady=6)
    botao_imprimir_ultima_etiqueta.grid(row=6, column=0, columnspan=3, padx=10, pady=(0,15), sticky="ew", ipady=4)

    aba.grid_columnconfigure(1, weight=2)
    aba.grid_columnconfigure(2, weight=1)

    # --- Bindings e Comandos ---
    ler_clientes_cb = ui_callbacks['ler_clientes']
    combo_remetente['postcommand'] = lambda: ui_helpers.atualizar_combobox_clientes(entry_pesquisa_remetente, combo_remetente, ler_clientes_cb)
    entry_pesquisa_remetente.bind("<KeyRelease>", lambda event: ui_event_handlers.handle_dynamic_client_search(event, entry_pesquisa_remetente, combo_remetente, ler_clientes_cb))

    combo_destinatario['postcommand'] = lambda: ui_helpers.atualizar_combobox_clientes(entry_pesquisa_destinatario, combo_destinatario, ler_clientes_cb)
    entry_pesquisa_destinatario.bind("<KeyRelease>", lambda event: ui_event_handlers.handle_dynamic_client_search(event, entry_pesquisa_destinatario, combo_destinatario, ler_clientes_cb))

    botao_gerar['command'] = lambda: ui_event_handlers.gerar_envelope(ui_elements, global_state, ui_callbacks, show_message_func)
    botao_imprimir_ultima_etiqueta['command'] = lambda: ui_event_handlers.imprimir_ultima_etiqueta(global_state, ui_callbacks, show_message_func)

    # --- Armazenar referências ---
    ui_elements.update({
        'combo_remetente': combo_remetente, 'entry_pesquisa_remetente': entry_pesquisa_remetente,
        'combo_destinatario': combo_destinatario, 'entry_pesquisa_destinatario': entry_pesquisa_destinatario,
        'combo_modalidade': combo_modalidade, 'combo_atendente': combo_atendente,
        'combo_tipo': combo_tipo, 'botao_gerar': botao_gerar,
        'botao_imprimir_ultima_etiqueta': botao_imprimir_ultima_etiqueta
    })

    return aba

def criar_aba_programado(notebook, global_state, ui_callbacks, ui_elements, show_message_func):
    """Cria e retorna a aba 'Programado' com o novo layout em grade."""
    aba = ttk.Frame(notebook, padding="10", style="Content.TFrame")

    # --- Frame Superior de Controles ---
    frame_superior_prog = ttk.Frame(aba, style="Content.TFrame")
    frame_superior_prog.pack(pady=(5,10), padx=0, fill=tk.X)

    ttk.Label(frame_superior_prog, text="Remetente:").pack(side=tk.LEFT, padx=(0, 5))
    combo_remetente_programado = ttk.Combobox(frame_superior_prog, width=30, state="readonly", font=('Segoe UI', 9))
    entry_pesquisa_remetente_programado = ttk.Entry(frame_superior_prog, width=20, font=('Segoe UI', 9))
    botao_buscar_programado = ttk.Button(frame_superior_prog, text="Buscar", style="Secondary.TButton")
    botao_refresh_programado = ttk.Button(frame_superior_prog, text="Atualizar", style="Secondary.TButton")

    ttk.Label(frame_superior_prog, text="Atendente:").pack(side=tk.LEFT, padx=(20,5))
    combo_atendente_prog = ttk.Combobox(frame_superior_prog, values=global_state['lista_atendentesb'], state="readonly", width=20, font=('Segoe UI', 9))

    combo_remetente_programado.pack(side=tk.LEFT, padx=0, fill=tk.X, expand=True)
    entry_pesquisa_remetente_programado.pack(side=tk.LEFT, padx=(5,0))
    botao_buscar_programado.pack(side=tk.LEFT, padx=(10, 5))
    botao_refresh_programado.pack(side=tk.LEFT, padx=(0, 10))
    combo_atendente_prog.pack(side=tk.LEFT, padx=5)

    # --- Frame Principal para a Lista de Envelopes com Scroll ---
    main_frame_prog = ttk.Frame(aba)
    main_frame_prog.pack(fill=tk.BOTH, expand=True)

    canvas_prog = tk.Canvas(main_frame_prog, bg=ui_elements.get('colors', {}).get("COR_FUNDO_FRAME", "#E0E0E0"))
    scrollbar_prog = ttk.Scrollbar(main_frame_prog, orient="vertical", command=canvas_prog.yview)

    # O frame_lista_prog é onde os widgets da grade serão colocados
    scrollable_frame_prog = ttk.Frame(canvas_prog, style="Content.TFrame")

    scrollable_frame_prog.bind("<Configure>", lambda e: canvas_prog.configure(scrollregion=canvas_prog.bbox("all")))
    canvas_prog_window = canvas_prog.create_window((0, 0), window=scrollable_frame_prog, anchor="nw")

    def configure_canvas_width(event):
        canvas_prog.itemconfig(canvas_prog_window, width=event.width)

    canvas_prog.bind("<Configure>", configure_canvas_width)
    canvas_prog.configure(yscrollcommand=scrollbar_prog.set)
    canvas_prog.pack(side="left", fill="both", expand=True)
    scrollbar_prog.pack(side="right", fill="y")

    canvas_prog.bind_all("<MouseWheel>", lambda event: canvas_prog.yview_scroll(int(-1*(event.delta/120)), "units"))

    # --- Bindings e Comandos ---
    ler_clientes_cb = ui_callbacks['ler_clientes']
    combo_remetente_programado['postcommand'] = lambda: ui_helpers.atualizar_combobox_clientes(entry_pesquisa_remetente_programado, combo_remetente_programado, ler_clientes_cb)
    entry_pesquisa_remetente_programado.bind("<KeyRelease>", lambda event: ui_event_handlers.handle_dynamic_client_search(event, entry_pesquisa_remetente_programado, combo_remetente_programado, ler_clientes_cb))
    botao_buscar_programado['command'] = lambda: ui_event_handlers.buscar_programados_ui(ui_elements, global_state, ui_callbacks, show_message_func)
    botao_refresh_programado['command'] = lambda: ui_event_handlers.refresh_programados_e_invalidar_cache(ui_elements, global_state, ui_callbacks, show_message_func)

    # --- Armazenar Referências ---
    ui_elements.update({
        'combo_remetente_programado': combo_remetente_programado,
        'entry_pesquisa_remetente_programado': entry_pesquisa_remetente_programado,
        'scrollable_frame_prog': scrollable_frame_prog,
        'combo_atendente_prog': combo_atendente_prog,
        'botao_refresh_programado': botao_refresh_programado
    })

    return aba

def criar_aba_saida(notebook, global_state, ui_callbacks, ui_elements, show_message_func):
    """Cria e retorna a aba 'Saída'."""
    aba = ttk.Frame(notebook, padding="15", style="Content.TFrame")

    frame_busca_saida = ttk.Frame(aba, style="Content.TFrame")
    frame_busca_saida.pack(pady=(10,10), padx=0, fill=tk.X)

    ttk.Label(frame_busca_saida, text="Cliente Destinatário:").pack(side=tk.LEFT, padx=(0, 10))
    combo_cliente_saida = ttk.Combobox(frame_busca_saida, width=30, state="readonly", font=('Segoe UI', 9))
    entry_pesquisa_cliente_saida = ttk.Entry(frame_busca_saida, width=20, font=('Segoe UI', 9))
    botao_buscar_saida = ttk.Button(frame_busca_saida, text="Buscar Pendentes", style="Secondary.TButton")

    combo_cliente_saida.pack(side=tk.LEFT, padx=0, fill=tk.X, expand=True)
    entry_pesquisa_cliente_saida.pack(side=tk.LEFT, padx=(10,0))
    botao_buscar_saida.pack(side=tk.LEFT, padx=(15, 0))

    frame_tree_saida = ttk.Frame(aba, style="Content.TFrame")
    frame_tree_saida.pack(expand=True, fill='both', pady=(10,0))

    colunas = ("Sel.", "Código", "Data Reg.", "Remetente", "Destinatário", "Modalidade", "Atendente", "Tipo Pacote")
    tree_saida = ttk.Treeview(frame_tree_saida, columns=colunas, show="headings", selectmode="none", style="Treeview")
    for col in colunas:
        w, minw, anchor, stretch = (100, 80, tk.W, tk.YES)
        if col == "Sel.": w, minw, stretch, anchor = (40, 40, tk.NO, tk.CENTER)
        elif col == "Código": w, minw, anchor = (80, 75, tk.CENTER)
        elif col == "Data Reg.": w, minw = (130, 120)
        elif col in ["Remetente", "Destinatário"]: w, minw = (170, 130)
        elif col == "Atendente": w, minw = (110, 100)
        tree_saida.heading(col, text=col)
        tree_saida.column(col, width=w, minwidth=minw, anchor=anchor, stretch=stretch)

    scrollbar_saida_y = ttk.Scrollbar(frame_tree_saida, orient="vertical", command=tree_saida.yview, style="Vertical.TScrollbar")
    tree_saida.configure(yscrollcommand=scrollbar_saida_y.set)
    scrollbar_saida_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree_saida.pack(side=tk.LEFT, expand=True, fill='both')

    frame_controles_saida = ttk.Frame(aba, style="Content.TFrame")
    frame_controles_saida.pack(fill=tk.X, pady=(10,10))

    ttk.Label(frame_controles_saida, text="Atendente da Saída:").pack(side=tk.LEFT, padx=(0,10))
    combo_atendente_saida = ttk.Combobox(frame_controles_saida, values=global_state['lista_atendentes'], state="readonly", width=20, font=('Segoe UI', 9))
    botao_dar_baixa = ttk.Button(frame_controles_saida, text="Dar Baixa nos Selecionados", style="Danger.TButton")

    combo_atendente_saida.pack(side=tk.LEFT, padx=5)
    botao_dar_baixa.pack(side=tk.LEFT, padx=(15, 0), expand=True, fill=tk.X, ipady=4)

    ler_clientes_cb = ui_callbacks['ler_clientes']
    combo_cliente_saida['postcommand'] = lambda: ui_helpers.atualizar_combobox_clientes(entry_pesquisa_cliente_saida, combo_cliente_saida, ler_clientes_cb)
    entry_pesquisa_cliente_saida.bind("<KeyRelease>", lambda event: ui_event_handlers.handle_dynamic_client_search(event, entry_pesquisa_cliente_saida, combo_cliente_saida, ler_clientes_cb))
    botao_buscar_saida['command'] = lambda: ui_event_handlers.buscar_envelopes_para_saida(ui_elements, global_state, ui_callbacks, show_message_func)
    tree_saida.bind("<ButtonRelease-1>", ui_event_handlers.toggle_checkbox_saida)
    botao_dar_baixa['command'] = lambda: ui_event_handlers.dar_baixa_envelopes(ui_elements, global_state, ui_callbacks, show_message_func)

    ui_elements.update({
        'combo_cliente_saida': combo_cliente_saida, 'entry_pesquisa_cliente_saida': entry_pesquisa_cliente_saida,
        'tree_saida': tree_saida, 'combo_atendente_saida': combo_atendente_saida
    })

    return aba

def criar_aba_cadastro(notebook, global_state, ui_callbacks, ui_elements, show_message_func):
    """Cria e retorna a aba 'Cadastro'."""
    aba = ttk.Frame(notebook, padding="20", style="Content.TFrame")

    frame_inputs = ttk.Frame(aba, style="Content.TFrame")
    frame_inputs.pack(fill=tk.X, pady=(0,10))

    ttk.Label(frame_inputs, text="Nome Completo:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
    entry_nome = ttk.Entry(frame_inputs, width=45, font=('Segoe UI', 9))
    entry_nome.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

    ttk.Label(frame_inputs, text="Telefone (com DDD):").grid(row=1, column=0, padx=10, pady=10, sticky="w")
    entry_telefone = ttk.Entry(frame_inputs, width=45, font=('Segoe UI', 9))
    entry_telefone.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

    ttk.Label(frame_inputs, text="NCliente:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
    entry_ncliente = ttk.Entry(frame_inputs, width=45, font=('Segoe UI', 9))
    entry_ncliente.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

    botao_cadastrar = ttk.Button(frame_inputs, text="Cadastrar/Atualizar Cliente", style="Primary.TButton")
    botao_cadastrar.grid(row=3, column=0, columnspan=2, padx=10, pady=20, sticky="ew", ipady=6)
    frame_inputs.grid_columnconfigure(1, weight=1)

    frame_tree = ttk.LabelFrame(aba, text="Clientes Cadastrados", padding="10", style="TLabelframe")
    frame_tree.pack(fill='both', expand=True, pady=(10,0))

    frame_busca = ttk.Frame(frame_tree, style="Content.TFrame")
    frame_busca.pack(fill=tk.X, pady=(0, 5))
    ttk.Label(frame_busca, text="Buscar Cliente:").pack(side=tk.LEFT, padx=(0, 5))
    entry_pesquisa_tree = ttk.Entry(frame_busca, width=40, font=('Segoe UI', 9))
    entry_pesquisa_tree.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

    colunas = ("Nome", "Telefone", "NCliente")
    tree_clientes = ttk.Treeview(frame_tree, columns=colunas, show="headings", selectmode="browse", style="Treeview")
    for col in colunas:
        w, minw, anchor = (180, 80, tk.W)
        if col == "Telefone": w = 100
        elif col == "NCliente": w, anchor = (80, tk.CENTER)
        tree_clientes.heading(col, text=col)
        tree_clientes.column(col, width=w, minwidth=minw, anchor=anchor, stretch=tk.YES)

    scrollbar_y = ttk.Scrollbar(frame_tree, orient="vertical", command=tree_clientes.yview, style="Vertical.TScrollbar")
    tree_clientes.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree_clientes.pack(expand=True, fill='both')

    botao_cadastrar['command'] = lambda: ui_event_handlers.salvar_cliente(ui_elements, ui_callbacks, show_message_func)
    tree_clientes.bind("<<TreeviewSelect>>", lambda event: ui_event_handlers.selecionar_cliente_para_edicao(event, ui_elements))
    entry_pesquisa_tree.bind("<KeyRelease>", lambda event: ui_event_handlers.filtrar_clientes_cadastro(event, ui_elements, ui_callbacks))

    ui_elements.update({
        'entry_nome_cadastro': entry_nome, 'entry_telefone_cadastro': entry_telefone,
        'entry_ncliente_cadastro': entry_ncliente, 'tree_clientes_cadastro': tree_clientes,
        'entry_pesquisa_cliente_cadastro_tree': entry_pesquisa_tree
    })

    return aba

def criar_aba_historico_entrada(notebook, global_state, ui_callbacks, ui_elements, show_message_func):
    """Cria e retorna a aba 'Histórico de Entrada'."""
    aba = ttk.Frame(notebook, padding="10", style="Content.TFrame")

    frame_filtros_master = ttk.Frame(aba, padding=(0,0), style="Content.TFrame")
    frame_filtros_master.pack(fill=tk.X, pady=(10,5))

    # --- Frame para filtros de data, remetente, destinatário ---
    frame_filtros_esquerda = ttk.Frame(frame_filtros_master, style="Content.TFrame")
    frame_filtros_esquerda.pack(side=tk.LEFT, fill=tk.X, expand=True)

    frame_filtro_data = ttk.Frame(frame_filtros_esquerda, style="Content.TFrame")
    frame_filtro_data.pack(fill=tk.X, pady=(0,8))
    ttk.Label(frame_filtro_data, text="Data Inicial (dd/mm/aaaa):").pack(side=tk.LEFT, padx=(0,5))
    entry_data_inicial = ttk.Entry(frame_filtro_data, width=12, font=('Segoe UI', 9))
    entry_data_inicial.pack(side=tk.LEFT, padx=(0,10))
    ttk.Label(frame_filtro_data, text="Data Final (dd/mm/aaaa):").pack(side=tk.LEFT, padx=(0,5))
    entry_data_final = ttk.Entry(frame_filtro_data, width=12, font=('Segoe UI', 9))
    entry_data_final.pack(side=tk.LEFT, padx=(0,15))

    frame_filtro_remetente = ttk.Frame(frame_filtros_esquerda, style="Content.TFrame")
    frame_filtro_remetente.pack(fill=tk.X, pady=(0,8))
    ttk.Label(frame_filtro_remetente, text="Remetente:").pack(side=tk.LEFT, padx=(0,5))
    combo_remetente = ttk.Combobox(frame_filtro_remetente, width=30, state="readonly", font=('Segoe UI', 9))
    entry_pesquisa_remetente = ttk.Entry(frame_filtro_remetente, width=20, font=('Segoe UI', 9))
    combo_remetente.pack(side=tk.LEFT, padx=(0,0))
    entry_pesquisa_remetente.pack(side=tk.LEFT, padx=(10,15))

    frame_filtro_dest = ttk.Frame(frame_filtros_esquerda, style="Content.TFrame")
    frame_filtro_dest.pack(fill=tk.X, pady=(0,10))
    ttk.Label(frame_filtro_dest, text="Destinatário:").pack(side=tk.LEFT, padx=(0,5))
    combo_dest = ttk.Combobox(frame_filtro_dest, width=30, state="readonly", font=('Segoe UI', 9))
    entry_pesquisa_dest = ttk.Entry(frame_filtro_dest, width=20, font=('Segoe UI', 9))
    combo_dest.pack(side=tk.LEFT, padx=(0,0))
    entry_pesquisa_dest.pack(side=tk.LEFT, padx=(10,15))

    frame_botoes = ttk.Frame(frame_filtros_esquerda, style="Content.TFrame")
    frame_botoes.pack(fill=tk.X, pady=(5,0))
    botao_aplicar = ttk.Button(frame_botoes, text="Aplicar Filtros", style="Primary.TButton")
    botao_limpar = ttk.Button(frame_botoes, text="Limpar Filtros", style="Secondary.TButton")
    botao_aplicar.pack(side=tk.LEFT, padx=(0,10))
    botao_limpar.pack(side=tk.LEFT, padx=0)

    # --- Frame para a contagem no canto superior direito ---
    frame_contagem = ttk.Frame(frame_filtros_master, style="Content.TFrame")
    frame_contagem.pack(side=tk.RIGHT, anchor=tk.NE, padx=(10, 0)) # Alinha à direita, topo

    # Variável para armazenar o texto da contagem
    strvar_contagem_hist_entrada = tk.StringVar(value="Exibindo: 0 envelopes")
    # Label para exibir a contagem
    label_contagem = ttk.Label(frame_contagem, textvariable=strvar_contagem_hist_entrada, anchor=tk.E, style="Note.TLabel")
    label_contagem.pack(pady=(5, 0)) # Adiciona um pouco de padding superior

    # --- Frame da Treeview ---
    frame_tree = ttk.Frame(aba, style="Content.TFrame")
    frame_tree.pack(expand=True, fill='both', pady=(10,0))

    colunas = ("Data Reg.", "Código", "Remetente", "Tel. Rem", "Destinatário", "Tel. Dest", "Modalidade", "Atendente Reg.", "Tipo Pacote")
    tree_historico = ttk.Treeview(frame_tree, columns=colunas, show="headings", style="Treeview")
    for col in colunas:
        w, minw, anchor = (95, 85, tk.W)
        if col == "Data Reg.": w, minw = (125, 115)
        elif col == "Código": w, minw, anchor = (75, 65, tk.CENTER)
        elif "Tel." in col: w, minw = (105, 95)
        elif col in ["Remetente", "Destinatário"]: w, minw = (155, 125)
        elif col == "Atendente Reg.": w, minw = (105, 95)
        tree_historico.heading(col, text=col)
        tree_historico.column(col, width=w, minwidth=minw, anchor=anchor, stretch=tk.YES)

    scrollbar_y = ttk.Scrollbar(frame_tree, orient="vertical", command=tree_historico.yview, style="Vertical.TScrollbar")
    scrollbar_x = ttk.Scrollbar(frame_tree, orient="horizontal", command=tree_historico.xview, style="Horizontal.TScrollbar")
    tree_historico.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    tree_historico.pack(expand=True, fill='both')

    # --- Bindings e Comandos ---
    ler_clientes_cb = ui_callbacks['ler_clientes']
    combo_remetente['postcommand'] = lambda: ui_helpers.atualizar_combobox_clientes(entry_pesquisa_remetente, combo_remetente, ler_clientes_cb)
    entry_pesquisa_remetente.bind("<KeyRelease>", lambda event: ui_event_handlers.handle_dynamic_client_search(event, entry_pesquisa_remetente, combo_remetente, ler_clientes_cb))
    combo_dest['postcommand'] = lambda: ui_helpers.atualizar_combobox_clientes(entry_pesquisa_dest, combo_dest, ler_clientes_cb)
    entry_pesquisa_dest.bind("<KeyRelease>", lambda event: ui_event_handlers.handle_dynamic_client_search(event, entry_pesquisa_dest, combo_dest, ler_clientes_cb))
    botao_aplicar['command'] = lambda: ui_event_handlers.aplicar_filtros_hist_entrada(ui_elements, ui_callbacks)
    botao_limpar['command'] = lambda: ui_event_handlers.resetar_filtros_hist_entrada(ui_elements, ui_callbacks)

    # --- Armazenar Referências ---
    ui_elements.update({
        'entry_data_inicial_hist': entry_data_inicial, 'entry_data_final_hist': entry_data_final,
        'combo_cliente_hist_entrada': combo_remetente, 'entry_pesquisa_cliente_hist_entrada': entry_pesquisa_remetente,
        'combo_dest_hist_entrada': combo_dest, 'entry_pesquisa_dest_hist_entrada': entry_pesquisa_dest,
        'tree_historico': tree_historico,
        # Adiciona a variável da string de contagem aos ui_elements
        'strvar_contagem_hist_entrada': strvar_contagem_hist_entrada,
        # Adiciona o label de contagem (opcional, pode não ser necessário referenciar diretamente)
        'label_contagem_hist_entrada': label_contagem
    })

    return aba

# CORREÇÃO: Adicionado o parâmetro 'show_message_func' aqui
def criar_aba_historico_saida(notebook, global_state, ui_callbacks, ui_elements, show_message_func):
    """Cria e retorna a aba 'Histórico de Saída'."""
    aba = ttk.Frame(notebook, padding="10", style="Content.TFrame")

    frame_filtro = ttk.Frame(aba, padding=(0,10), style="Content.TFrame")
    frame_filtro.pack(fill=tk.X, pady=(10,5))
    ttk.Label(frame_filtro, text="Cliente Destinatário:").pack(side=tk.LEFT, padx=(0,10))
    combo_cliente = ttk.Combobox(frame_filtro, width=30, state="readonly", font=('Segoe UI', 9))
    entry_pesquisa = ttk.Entry(frame_filtro, width=20, font=('Segoe UI', 9))
    botao_filtrar = ttk.Button(frame_filtro, text="Filtrar por Cliente", style="Primary.TButton")
    botao_limpar = ttk.Button(frame_filtro, text="Limpar Filtro", style="Secondary.TButton")

    combo_cliente.pack(side=tk.LEFT, padx=0)
    entry_pesquisa.pack(side=tk.LEFT, padx=(10,10))
    botao_filtrar.pack(side=tk.LEFT, padx=10)
    botao_limpar.pack(side=tk.LEFT, padx=5)

    frame_tree = ttk.Frame(aba, style="Content.TFrame")
    frame_tree.pack(expand=True, fill='both', pady=(10,0))

    colunas = ("Data Saída", "Código", "Destinatário", "Tel. Dest.", "Remetente", "Data Reg. Orig.", "Atendente Reg. Original", "Atendente Saída")
    tree_historico = ttk.Treeview(frame_tree, columns=colunas, show="headings", style="Treeview")
    for col in colunas:
        w, minw, anchor = (105, 85, tk.W)
        if col == "Data Saída": w, minw = (125, 115)
        elif col == "Código": w, minw, anchor = (80, 70, tk.CENTER)
        elif col == "Destinatário": w, minw = (160, 130)
        elif col == "Tel. Dest.": w, minw = (110, 100)
        elif col == "Remetente": w, minw = (160, 130)
        elif col == "Data Reg. Orig.": w, minw = (125, 115)
        elif col == "Atendente Reg. Original": w, minw = (140, 120)
        elif col == "Atendente Saída": w, minw = (115, 95)
        tree_historico.heading(col, text=col)
        tree_historico.column(col, width=w, minwidth=minw, anchor=anchor, stretch=tk.YES)

    scrollbar_y = ttk.Scrollbar(frame_tree, orient="vertical", command=tree_historico.yview, style="Vertical.TScrollbar")
    scrollbar_x = ttk.Scrollbar(frame_tree, orient="horizontal", command=tree_historico.xview, style="Horizontal.TScrollbar")
    tree_historico.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
    tree_historico.pack(expand=True, fill='both')

    ler_clientes_cb = ui_callbacks['ler_clientes']
    combo_cliente['postcommand'] = lambda: ui_helpers.atualizar_combobox_clientes(entry_pesquisa, combo_cliente, ler_clientes_cb)
    entry_pesquisa.bind("<KeyRelease>", lambda event: ui_event_handlers.handle_dynamic_client_search(event, entry_pesquisa, combo_cliente, ler_clientes_cb))
    botao_filtrar['command'] = lambda: ui_event_handlers.aplicar_filtro_cliente_hist_saida(ui_elements, ui_callbacks)
    botao_limpar['command'] = lambda: ui_event_handlers.resetar_filtro_cliente_hist_saida(ui_elements, ui_callbacks)

    ui_elements.update({
        'combo_cliente_hist_saida': combo_cliente, 'entry_pesquisa_cliente_hist_saida': entry_pesquisa,
        'tree_historico_saida': tree_historico
    })

    return aba

def criar_aba_creditos(notebook, global_state, ui_callbacks, ui_elements, show_message_func):
    """Cria e retorna a aba 'Créditos'."""
    aba = ttk.Frame(notebook, padding="20", style="Content.TFrame")

    frame_input = ttk.Frame(aba, style="Content.TFrame")
    frame_input.pack(fill=tk.X, pady=(10, 10))
    ttk.Label(frame_input, text="NCliente:").pack(side=tk.LEFT, padx=(0, 10))
    entry_ncliente = ttk.Entry(frame_input, width=40, font=('Segoe UI', 9))
    entry_ncliente.pack(side=tk.LEFT, padx=0, fill=tk.X, expand=True)

    frame_botoes = ttk.Frame(aba, style="Content.TFrame")
    frame_botoes.pack(fill=tk.X, pady=(10, 20))
    botao_add = ttk.Button(frame_botoes, text="Adicionar Crédito (URL)", style="Primary.TButton")
    botao_rem = ttk.Button(frame_botoes, text="Remover Créditos (URL)", style="Danger.TButton")
    botao_add.pack(side=tk.LEFT, padx=(0, 10), expand=True, fill=tk.X, ipady=6)
    botao_rem.pack(side=tk.LEFT, padx=(10, 0), expand=True, fill=tk.X, ipady=6)

    frame_tree = ttk.LabelFrame(aba, text="Clientes com NCliente", padding="10", style="TLabelframe")
    frame_tree.pack(fill='both', expand=True, pady=(10,0))

    colunas = ("Nome", "NCliente")
    tree_creditos = ttk.Treeview(frame_tree, columns=colunas, show="headings", selectmode="browse", style="Treeview")
    for col in colunas:
        w, minw, anchor = (200, 80, tk.W)
        if col == "NCliente": w, anchor = (100, tk.CENTER)
        tree_creditos.heading(col, text=col)
        tree_creditos.column(col, width=w, minwidth=minw, anchor=anchor, stretch=tk.YES)

    scrollbar_y = ttk.Scrollbar(frame_tree, orient="vertical", command=tree_creditos.yview, style="Vertical.TScrollbar")
    tree_creditos.configure(yscrollcommand=scrollbar_y.set)
    scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
    tree_creditos.pack(expand=True, fill='both')

    botao_add['command'] = lambda: ui_event_handlers.abrir_url_credito(ui_elements, 'add', show_message_func)
    botao_rem['command'] = lambda: ui_event_handlers.abrir_url_credito(ui_elements, 'remove', show_message_func)
    tree_creditos.bind("<<TreeviewSelect>>", lambda event: ui_event_handlers.selecionar_credito_para_edicao(event, ui_elements))

    ui_elements.update({
        'entry_ncliente_creditos': entry_ncliente,
        'tree_creditos': tree_creditos
    })

    return aba

def criar_aba_configuracoes(notebook, global_state, ui_callbacks, ui_elements, show_message_func):
    """Cria e retorna a aba 'Configurações'."""
    aba = ttk.Frame(notebook, padding="20", style="Content.TFrame")

    # --- Variáveis de Controle ---
    strvar_printer = tk.StringVar(value=global_state.get('selected_printer_name', ''))
    boolvar_printing = tk.BooleanVar(value=global_state.get('g_enable_printing', True))
    strvar_font_dest = tk.StringVar(value=str(global_state.get('g_font_size_dest_pts', 7)))
    strvar_font_code = tk.StringVar(value=str(global_state.get('g_font_size_code_pts', 20)))
    strvar_font_data = tk.StringVar(value=str(global_state.get('g_font_size_data_pts', 10)))
    strvar_spacing = tk.StringVar(value=str(global_state.get('g_line_spacing_mm', 1.0)))

    # --- Frames ---
    frame_db = ttk.LabelFrame(aba, text="Informações do Banco de Dados", padding="15", style="TLabelframe")
    frame_printer = ttk.LabelFrame(aba, text="Configuração da Impressora", padding="15", style="TLabelframe")
    frame_visual = ttk.LabelFrame(aba, text="Configurações Visuais da Etiqueta", padding="15", style="TLabelframe")
    frame_buttons = ttk.Frame(aba, style="Content.TFrame")

    frame_db.pack(fill=tk.X, pady=5)
    frame_printer.pack(fill=tk.X, pady=7)
    frame_visual.pack(fill=tk.X, pady=5)
    frame_buttons.pack(fill=tk.X, pady=(8,0))

    # --- Widgets ---
    ttk.Label(frame_printer, text="Impressora de Etiquetas:").grid(row=0, column=0, padx=5, pady=8, sticky="w")
    combo_printer = ttk.Combobox(frame_printer, textvariable=strvar_printer, width=57, state="readonly" if global_state.get('PYWIN32_AVAILABLE') else "disabled", font=('Segoe UI', 9))
    combo_printer.grid(row=0, column=1, padx=5, pady=8, sticky="ew")
    check_printing = ttk.Checkbutton(frame_printer, text="Habilitar impressão automática de etiquetas", variable=boolvar_printing, style="TCheckbutton")
    check_printing.grid(row=1, column=0, columnspan=2, padx=5, pady=10, sticky="w")
    frame_printer.grid_columnconfigure(1, weight=1)

    ttk.Label(frame_visual, text="Tam. Fonte Destinatário (pts):").grid(row=0, column=0, padx=5, pady=6, sticky="w")
    entry_font_dest = ttk.Entry(frame_visual, textvariable=strvar_font_dest, width=8, font=('Segoe UI', 9))
    entry_font_dest.grid(row=0, column=1, padx=5, pady=6, sticky="ew")
    ttk.Label(frame_visual, text="Tam. Fonte Código (pts):").grid(row=1, column=0, padx=5, pady=6, sticky="w")
    entry_font_code = ttk.Entry(frame_visual, textvariable=strvar_font_code, width=8, font=('Segoe UI', 9))
    entry_font_code.grid(row=1, column=1, padx=5, pady=6, sticky="ew")
    ttk.Label(frame_visual, text="Tam. Fonte Data/Hora (pts):").grid(row=2, column=0, padx=5, pady=6, sticky="w")
    entry_font_data = ttk.Entry(frame_visual, textvariable=strvar_font_data, width=8, font=('Segoe UI', 9))
    entry_font_data.grid(row=2, column=1, padx=5, pady=6, sticky="ew")
    ttk.Label(frame_visual, text="Espaçamento Linhas (mm):").grid(row=3, column=0, padx=5, pady=6, sticky="w")
    entry_spacing = ttk.Entry(frame_visual, textvariable=strvar_spacing, width=8, font=('Segoe UI', 9))
    entry_spacing.grid(row=3, column=1, padx=5, pady=6, sticky="ew")
    frame_visual.grid_columnconfigure(1, weight=1)

    btn_save = ttk.Button(frame_buttons, text="Salvar TODAS as Configurações", style="Primary.TButton")
    btn_save.pack(pady=(10, 5), ipady=4, expand=True, fill=tk.X)

    label_note = ttk.Label(aba, text="Nota: Todas as configurações são salvas em 'config.ini'.\nPara que alterações de CORES tenham efeito completo, pode ser necessário reiniciar a aplicação.", wraplength=600, justify=tk.LEFT, style="Note.TLabel")
    label_note.pack(pady=(15,0), anchor="w")

    # --- Comandos e Bindings ---
    btn_save['command'] = lambda: ui_event_handlers.salvar_configuracoes(ui_elements, global_state, ui_callbacks, show_message_func)
    # Atualiza estado dos botões de impressão na aba Entrada quando o check é alterado
    check_printing['command'] = lambda: ui_helpers.atualizar_estado_botoes_impressao(ui_elements, global_state)

    # --- Armazenar Referências ---
    ui_elements.update({
        'frame_config_db_info': frame_db,
        'combo_cfg_printer': combo_printer,
        'label_config_note': label_note,
        'strvar_selected_printer': strvar_printer,
        'boolvar_enable_printing': boolvar_printing,
        'strvar_font_dest': strvar_font_dest,
        'strvar_font_code': strvar_font_code,
        'strvar_font_data': strvar_font_data,
        'strvar_line_spacing': strvar_spacing
    })

    return aba