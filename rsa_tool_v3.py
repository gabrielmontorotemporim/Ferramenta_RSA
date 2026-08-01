import customtkinter as ctk

# ─── Importa TODAS as funções matemáticas do seu módulo ──────────────────────
from funcoes_rsa import (
    e_primo,
    calcular_mdc,
    gerar_expoente_publico,
    inverso_modular_estendido,
    transformar_em_numeros,
    quebrar_em_blocos,
    codificar_blocos,
    decodificar_blocos,
    transformar_em_texto,
)

# ─── Tema ────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

BG_MAIN      = "#0d1117"
BG_PANEL     = "#161b22"
BG_CARD      = "#0d1117"
BG_INPUT     = "#21262d"
FG_WHITE     = "#e6edf3"
FG_GRAY      = "#8b949e"
FG_GREEN     = "#3fb950"
FG_YELLOW    = "#d29922"
FG_CYAN      = "#58a6ff"
FG_ORANGE    = "#f0883e"
ACCENT_GREEN = "#238636"
ACCENT_BLUE  = "#1f6feb"
ACCENT_GRAY  = "#30363d"
BORDER_COLOR = "#30363d"

# ─── Tamanhos de fonte (aumentados em 2px em relação à versão anterior) ──────
F_SMALL  = 16
F_NORMAL = 17
F_MEDIUM = 18
F_LARGE  = 19
F_TITLE  = 27
F_VER    = 18
F_STATUS = 16

# ─── Variáveis globais de interface ──────────────────────────────────────────
entry_p = entry_q = entry_n = entry_phi = entry_e = None
entry_pub = entry_priv = None
enc_pubkey = enc_plain = None
enc_out_numeros = enc_out_blocos = enc_out_cifrado = None
dec_privkey = dec_cipher = None
dec_out_blocos_q = dec_out_blocos_dec = dec_out_texto = None
status_lbl = status_tag = None
priv_visivel   = True   # controla visibilidade na coluna Geração de Chaves
dec_priv_visivel = True # controla visibilidade na coluna Decifrar

# ═════════════════════════════════════════════════════════════════════════════
# LÓGICA RSA  —  usa exclusivamente as funções de funcoes_rsa.py
# ═════════════════════════════════════════════════════════════════════════════

def gerar_chaves():
    """
    Fluxo de geração de chaves RSA:
      1. Lê p e q da interface.
      2. Valida primalidade com e_primo().
      3. Calcula n = p*q  e  φ(n) = (p-1)*(q-1).
      4. Gera e automaticamente com gerar_expoente_publico(φ(n)).
      5. Calcula d = inverso_modular_estendido(e, φ(n)).
      6. Preenche todos os campos de saída.
    """
    try:
        p = int(entry_p.get())
        q = int(entry_q.get())
    except ValueError:
        update_status("⚠  Insira valores inteiros para p e q.", ok=False)
        return

    if not e_primo(p):
        update_status(f"⚠  {p} não é primo.", ok=False); return
    if not e_primo(q):
        update_status(f"⚠  {q} não é primo.", ok=False); return
    if p == q:
        update_status("⚠  p e q devem ser distintos.", ok=False); return

    n   = p * q
    phi = (p - 1) * (q - 1)

    # e gerado automaticamente pela sua função
    e = gerar_expoente_publico(phi)
    if e is None:
        update_status("⚠  Não foi possível gerar e automaticamente.", ok=False); return

    # d = inverso modular de e módulo φ(n)
    d = inverso_modular_estendido(e, phi)

    # — preenche campos de geração —
    set_entry_val(entry_n,    str(n))
    set_entry_val(entry_phi,  str(phi))
    set_entry_val(entry_e,    str(e))
    set_entry_val(entry_pub,  f"{e}, {n}")
    set_entry_val(entry_priv, f"{d}, {n}")

    # — propaga chaves para as colunas de cifrar/decifrar —
    write_entry_val(enc_pubkey,  f"{e}, {n}")
    write_entry_val(dec_privkey, f"{d}, {n}")

    update_status(f"✔  Chaves geradas!   n = {n}   |   e = {e}   |   d = {d}")


def cifrar_mensagem():
    """
    Fluxo de cifragem RSA — exibe cada etapa na interface:
      Etapa 1 → sequência numérica   (transformar_em_numeros)
      Etapa 2 → blocos antes de cifrar (quebrar_em_blocos)
      Etapa 3 → blocos cifrados finais (codificar_blocos)  C = M^e mod n
    """
    try:
        raw = enc_pubkey.get().replace(" ", "")
        e_val, n_val = map(int, raw.split(","))
    except Exception:
        update_status("⚠  Chave pública inválida. Use o formato:  e, n", ok=False); return

    msg = enc_plain.get("1.0", "end").strip()
    if not msg:
        update_status("⚠  Escreva uma mensagem para cifrar.", ok=False); return

    # Etapa 1 — converte mensagem para representação numérica
    sequencia = transformar_em_numeros(msg)
    if sequencia == "erro":
        update_status(
            "⚠  Caractere não suportado. Use apenas letras (a–z) e espaços.",
            ok=False
        ); return

    # Etapa 2 — quebra em blocos que cabem em n
    blocos = quebrar_em_blocos(sequencia, n_val)

    # Etapa 3 — cifra: C = M^e mod n
    blocos_cifrados = codificar_blocos(blocos, e_val, n_val)

    # — preenche os três campos de saída —
    set_textbox_val(enc_out_numeros, sequencia)
    set_textbox_val(enc_out_blocos,  "  |  ".join(blocos))
    set_textbox_val(enc_out_cifrado, " ".join(str(c) for c in blocos_cifrados))

    update_status(
        f"✔  Mensagem cifrada!   {len(blocos)} bloco(s) gerado(s)."
    )


def decifrar_mensagem():
    """
    Fluxo de decifragem RSA — exibe cada etapa na interface:
      Etapa 1 → lista de blocos cifrados recebidos
      Etapa 2 → blocos decifrados (M = C^d mod n)
      Etapa 3 → mensagem em texto reconstituída
    """

    try:
        if not dec_priv_visivel and hasattr(dec_privkey, "_valor_real"):
            raw = dec_privkey._valor_real.replace(" ", "")
        else:
            raw = dec_privkey.get().replace(" ", "")
        d_val, n_val = map(int, raw.split(","))
    except Exception:
        update_status("⚠  Chave privada inválida. Use o formato:  d, n", ok=False); return

    texto_cifrado = dec_cipher.get("1.0", "end").strip()
    if not texto_cifrado:
        update_status("⚠  Cole os blocos cifrados (números separados por espaço).", ok=False); return

    try:
        lista_cifrada = [int(x) for x in texto_cifrado.split()]
    except ValueError:
        update_status("⚠  O texto cifrado deve conter apenas números inteiros.", ok=False); return

    # Etapa 1 — blocos cifrados recebidos (já exibidos no campo de entrada,
    #           mas mostramos formatados aqui para clareza)
    set_textbox_val(
        dec_out_blocos_q,
        "  |  ".join(str(c) for c in lista_cifrada)
    )

    # Etapa 2 — decifra: M = C^d mod n
    blocos_decifrados = decodificar_blocos(lista_cifrada, d_val, n_val)
    set_textbox_val(
        dec_out_blocos_dec,
        "  |  ".join(blocos_decifrados)
    )

    # Etapa 3 — reconstrói o texto original
    sequencia_recuperada = "".join(blocos_decifrados)
    mensagem = transformar_em_texto(sequencia_recuperada)
    set_textbox_val(dec_out_texto, mensagem)

    update_status(
        f"✔  Mensagem decifrada!   {len(lista_cifrada)} bloco(s) processado(s)."
    )


# ═════════════════════════════════════════════════════════════════════════════
# HELPERS DE INTERFACE
# ═════════════════════════════════════════════════════════════════════════════

def set_entry_val(w: ctk.CTkEntry, val: str):
    """Escreve em CTkEntry somente-leitura."""
    w.configure(state="normal")
    w.delete(0, "end")
    w.insert(0, val)
    w.configure(state="readonly")

def set_textbox_val(w: ctk.CTkTextbox, val: str):
    """Escreve em CTkTextbox somente-leitura."""
    w.configure(state="normal")
    w.delete("1.0", "end")
    w.insert("1.0", val)
    w.configure(state="disabled")

def write_entry_val(w: ctk.CTkEntry, val: str):
    """Escreve em CTkEntry editável."""
    w.delete(0, "end")
    w.insert(0, val)

def update_status(msg: str, ok: bool = True):
    status_lbl.configure(text="  " + msg + "  ")
    status_tag.configure(
        text=" ✔ OK " if ok else " ✖ Erro ",
        text_color=FG_GREEN if ok else "#f85149"
    )

def limpar_tudo():
    """
    Limpa todos os campos da interface e restaura o estado inicial.
    — Campos editáveis  → apagados
    — Campos readonly   → voltam ao placeholder (—)
    — Textboxes de saída → esvaziados
    — Visibilidade das chaves privadas → restaurada (mostrar)
    — Status → mensagem padrão
    """
    global priv_visivel, dec_priv_visivel

    # ── Coluna Geração de Chaves ──────────────────────────────────────────
    for w in (entry_p, entry_q):          # editáveis
        w.delete(0, "end")
    for w in (entry_n, entry_phi, entry_e, entry_pub, entry_priv):  # readonly
        set_entry_val(w, "")

    # garante que chave privada volta a aparecer
    if not priv_visivel:
        if hasattr(entry_priv, "_valor_real"):
            del entry_priv._valor_real
        priv_visivel = True

    # ── Coluna Cifrar ─────────────────────────────────────────────────────
    enc_pubkey.delete(0, "end")
    enc_plain.configure(state="normal")
    enc_plain.delete("1.0", "end")
    for w in (enc_out_numeros, enc_out_blocos, enc_out_cifrado):
        set_textbox_val(w, "")

    # ── Coluna Decifrar ───────────────────────────────────────────────────
    dec_privkey.delete(0, "end")
    if hasattr(dec_privkey, "_valor_real"):
        del dec_privkey._valor_real
    dec_priv_visivel = True

    dec_cipher.configure(state="normal")
    dec_cipher.delete("1.0", "end")
    for w in (dec_out_blocos_q, dec_out_blocos_dec, dec_out_texto):
        set_textbox_val(w, "")

    # ── Status ────────────────────────────────────────────────────────────
    status_lbl.configure(text="  Calculadora RSA pronta.  ")
    status_tag.configure(text=" ✔ Conectado ", text_color=FG_GREEN)


def _aplicar_visibilidade(widget: "ctk.CTkEntry", visivel: bool, btn: "ctk.CTkButton"):
    """
    Alterna o campo entre texto normal e caracteres mascarados (•).
    - visivel=True  → mostra o valor real
    - visivel=False → substitui cada dígito por '•'
    Atualiza o texto e o emoji do botão.
    """
    valor_atual = widget.cget("placeholder_text")  # fallback seguro

    # lê o valor real armazenado no campo (funciona mesmo em readonly)
    widget.configure(state="normal")
    valor_atual = widget.get()

    if visivel:
        # mostra o valor real — apenas garante que está em texto normal
        widget.delete(0, "end")
        widget.insert(0, valor_atual)
        btn.configure(text="🙈")
    else:
        # mascara: troca cada caractere por '•'
        widget.delete(0, "end")
        widget.insert(0, "•" * len(valor_atual))
        btn.configure(text="👁")

    widget.configure(state="readonly")


def toggle_priv_keygen(btn: "ctk.CTkButton"):
    """
    Chamada pelo botão da coluna Geração de Chaves.
    Alterna priv_visivel e reaplica a visibilidade em entry_priv.
    """
    global priv_visivel

    # lemos o valor real ANTES de mascarar (se já estiver mascarado,
    # pegamos do campo entry_pub que sempre fica visível e tem o mesmo n)
    if priv_visivel:
        # vamos mascarar: salvamos o valor real num atributo auxiliar
        entry_priv._valor_real = entry_priv.get()

    priv_visivel = not priv_visivel

    # restaura o valor real antes de aplicar a lógica
    entry_priv.configure(state="normal")
    if hasattr(entry_priv, "_valor_real"):
        entry_priv.delete(0, "end")
        entry_priv.insert(0, entry_priv._valor_real)
    entry_priv.configure(state="readonly")

    _aplicar_visibilidade(entry_priv, priv_visivel, btn)


def toggle_priv_decrypt(btn: "ctk.CTkButton"):
    """
    Chamada pelo botão da coluna Decifrar Mensagem.
    Alterna dec_priv_visivel e reaplica a visibilidade em dec_privkey.
    ATENÇÃO: dec_privkey é editável, então a lógica é ligeiramente diferente.
    """
    global dec_priv_visivel

    if dec_priv_visivel:
        # salva valor real antes de mascarar
        dec_privkey._valor_real = dec_privkey.get()
        dec_priv_visivel = False
        mascara = "•" * len(dec_privkey._valor_real)
        dec_privkey.delete(0, "end")
        dec_privkey.insert(0, mascara)
        btn.configure(text="👁")
    else:
        # restaura valor real
        dec_priv_visivel = True
        dec_privkey.delete(0, "end")
        if hasattr(dec_privkey, "_valor_real"):
            dec_privkey.insert(0, dec_privkey._valor_real)
        btn.configure(text="🙈")


# ═════════════════════════════════════════════════════════════════════════════
# CONSTRUTORES DE WIDGETS
# ═════════════════════════════════════════════════════════════════════════════

def create_scrollable_panel(parent, grid_col: int, padx=(5, 5)) -> ctk.CTkFrame:
    outer = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=10,
                         border_width=1, border_color=BORDER_COLOR)
    outer.grid(row=0, column=grid_col, padx=padx, pady=(8, 8), sticky="nsew")
    outer.grid_columnconfigure(0, weight=1)
    outer.grid_rowconfigure(0, weight=1)

    scroll = ctk.CTkScrollableFrame(outer, fg_color="transparent",
                                    scrollbar_button_color=BORDER_COLOR)
    scroll.grid(row=0, column=0, padx=3, pady=3, sticky="nsew")
    scroll.grid_columnconfigure(0, weight=1)

    inner = ctk.CTkFrame(scroll, fg_color="transparent")
    inner.grid(row=0, column=0, padx=10, pady=6, sticky="nsew")
    inner.grid_columnconfigure(0, weight=1)
    return inner

def create_section_title(parent, text: str, color: str):
    ctk.CTkLabel(parent, text=text,
                 font=ctk.CTkFont(size=F_LARGE, weight="bold"),
                 text_color=color).pack(anchor="w", pady=(0, 4))
    ctk.CTkFrame(parent, fg_color=BORDER_COLOR, height=1).pack(fill="x", pady=(0, 8))

def create_field_label(parent, text: str, color: str = FG_GRAY):
    ctk.CTkLabel(parent, text=text,
                 font=ctk.CTkFont(size=F_SMALL),
                 text_color=color, anchor="w"
                 ).pack(anchor="w", pady=(0, 2))

def create_step_label(parent, text: str, color: str):
    """Rótulo de etapa com destaque de cor."""
    ctk.CTkLabel(parent, text=text,
                 font=ctk.CTkFont(size=F_SMALL, weight="bold"),
                 text_color=color, anchor="w"
                 ).pack(anchor="w", pady=(4, 2))

def create_entry(parent, placeholder: str, ro: bool = False) -> ctk.CTkEntry:
    return ctk.CTkEntry(
        parent, placeholder_text=placeholder,
        fg_color=BG_INPUT, text_color=FG_WHITE,
        placeholder_text_color=FG_GRAY,
        border_color=BORDER_COLOR, border_width=1,
        corner_radius=6, height=34,
        font=ctk.CTkFont(size=F_NORMAL),
        state="readonly" if ro else "normal",
    )

def create_textbox(parent, height: int = 60, ro: bool = False,
                   text_color: str = FG_WHITE) -> ctk.CTkTextbox:
    return ctk.CTkTextbox(
        parent, height=height,
        fg_color=BG_INPUT, text_color=text_color,
        border_color=BORDER_COLOR, border_width=1,
        corner_radius=6, font=ctk.CTkFont(size=F_NORMAL),
        state="disabled" if ro else "normal",
    )

def create_divider(parent):
    """Seta indicando progressão entre etapas."""
    ctk.CTkLabel(parent, text="▼",
                 font=ctk.CTkFont(size=14),
                 text_color=BORDER_COLOR).pack(anchor="center", pady=(2, 0))


# ═════════════════════════════════════════════════════════════════════════════
# CONSTRUÇÃO DOS PAINÉIS
# ═════════════════════════════════════════════════════════════════════════════

def build_header(parent):
    hdr = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=0, border_width=0)
    hdr.grid(row=0, column=0, sticky="ew")
    hdr.grid_columnconfigure(0, weight=1)

    ctk.CTkFrame(hdr, fg_color=ACCENT_BLUE, height=3,
                 corner_radius=0).grid(row=0, column=0, sticky="ew")

    content = ctk.CTkFrame(hdr, fg_color="transparent")
    content.grid(row=1, column=0, padx=32, pady=(10, 8), sticky="ew")
    content.grid_columnconfigure(0, weight=1)

    title_row = ctk.CTkFrame(content, fg_color="transparent")
    title_row.grid(row=0, column=0, sticky="w")
    ctk.CTkLabel(title_row, text="🔐  Ferramenta Criptográfica RSA",
                 font=ctk.CTkFont(size=F_TITLE, weight="bold"),
                 text_color=FG_WHITE).pack(side="left")
    ctk.CTkLabel(title_row, text="  v1.3",
                 font=ctk.CTkFont(size=F_VER),
                 text_color=FG_GRAY).pack(side="left", pady=(4, 0))

    ctk.CTkLabel(
        content,
        text=(
            "Demonstração interativa do algoritmo RSA — gere suas chaves, cifre e decifre mensagens passo a passo.\n"
            "Escolha dois números primos (p, q) e clique em Gerar. O expoente público e é calculado automaticamente. \n"
            "Atenção: a ferramenta suporta apenas letras minúsculas (a–z) e espaços."
        ),
        font=ctk.CTkFont(size=F_NORMAL), text_color=FG_GRAY,
        justify="left", anchor="w", wraplength=1050,
    ).grid(row=1, column=0, sticky="w", pady=(4, 0))

    ctk.CTkFrame(hdr, fg_color=BORDER_COLOR, height=1,
                 corner_radius=0).grid(row=2, column=0, sticky="ew")


# ── Coluna 0: Geração de Chaves ───────────────────────────────────────────────

def build_keygen_col(parent):
    global entry_p, entry_q, entry_n, entry_phi, entry_e, entry_pub, entry_priv

    col = create_scrollable_panel(parent, grid_col=0, padx=(14, 5))
    create_section_title(col, "🔑  Geração de Chaves", FG_YELLOW)

    create_field_label(col, "Números primos  p  e  q")
    pq = ctk.CTkFrame(col, fg_color="transparent")
    pq.pack(fill="x", pady=(0, 6))
    pq.grid_columnconfigure((0, 1), weight=1)
    entry_p = create_entry(pq, "ex: 61")
    entry_p.grid(row=0, column=0, padx=(0, 4), sticky="ew")
    entry_q = create_entry(pq, "ex: 53")
    entry_q.grid(row=0, column=1, padx=(4, 0), sticky="ew")

    create_field_label(col, "n  (módulo  =  p × q)")
    entry_n = create_entry(col, "—", ro=True)
    entry_n.pack(fill="x", pady=(0, 6))

    create_field_label(col, "φ(n)  (totiente  =  (p−1)(q−1))")
    entry_phi = create_entry(col, "—", ro=True)
    entry_phi.pack(fill="x", pady=(0, 6))

    create_field_label(col, "Expoente público  e  (gerado automaticamente)")
    entry_e = create_entry(col, "—", ro=True)
    entry_e.pack(fill="x", pady=(0, 10))

    ctk.CTkButton(
        col, text="🔑  GERAR CHAVES RSA",
        font=ctk.CTkFont(size=F_MEDIUM, weight="bold"),
        fg_color=ACCENT_BLUE, hover_color="#1a5bb5",
        height=40, corner_radius=8,
        command=gerar_chaves
    ).pack(fill="x", pady=(0, 10))

    box = ctk.CTkFrame(col, fg_color=BG_CARD, corner_radius=8,
                       border_width=1, border_color=BORDER_COLOR)
    box.pack(fill="x")

    ctk.CTkLabel(box, text="SUAS CHAVES RSA",
                 font=ctk.CTkFont(size=F_SMALL, weight="bold"),
                 text_color=FG_WHITE).pack(anchor="w", padx=12, pady=(8, 4))

    ctk.CTkLabel(box, text="CHAVE PÚBLICA  (e, n)",
                 font=ctk.CTkFont(size=F_SMALL, weight="bold"),
                 text_color=FG_CYAN).pack(anchor="w", padx=12)
    entry_pub = create_entry(box, "ex: 17, 3233", ro=True)
    entry_pub.pack(fill="x", padx=12, pady=(2, 6))

    # ── CHAVE PRIVADA com botão de visibilidade ───────────────────────────
    # Criamos uma linha (row_priv) com o label à esquerda e o botão à direita
    row_priv = ctk.CTkFrame(box, fg_color="transparent")
    row_priv.pack(fill="x", padx=12, pady=(2, 0))

    ctk.CTkLabel(row_priv, text="CHAVE PRIVADA  (d, n)",
                 font=ctk.CTkFont(size=F_SMALL, weight="bold"),
                 text_color=FG_YELLOW).pack(side="left")

    # Botão criado antes de passar como argumento para o lambda
    btn_priv_keygen = ctk.CTkButton(
        row_priv, text="🙈",
        width=34, height=26, corner_radius=6,
        font=ctk.CTkFont(size=14),
        fg_color=ACCENT_GRAY, hover_color="#4a4f57",
        # lambda captura btn_priv_keygen por referência após sua criação
        command=lambda: toggle_priv_keygen(btn_priv_keygen)
    )
    btn_priv_keygen.pack(side="right")

    entry_priv = create_entry(box, "ex: 2753, 3233", ro=True)
    entry_priv.pack(fill="x", padx=12, pady=(2, 8))
    # ─────────────────────────────────────────────────────────────────────


# ── Coluna 1: Cifrar Mensagem ─────────────────────────────────────────────────

def build_encrypt_col(parent):
    global enc_pubkey, enc_plain
    global enc_out_numeros, enc_out_blocos, enc_out_cifrado

    col = create_scrollable_panel(parent, grid_col=1, padx=(5, 5))
    create_section_title(col, "🔒  Cifrar Mensagem", FG_GREEN)

    create_field_label(col, "Chave pública do destinatário  (e, n)")
    enc_pubkey = create_entry(col, "ex: 17, 3233")
    enc_pubkey.pack(fill="x", pady=(0, 8))

    create_field_label(col, "Mensagem em texto simples  (letras a–z e espaços)")
    enc_plain = create_textbox(col, height=100)
    enc_plain.pack(fill="x", pady=(0, 10))

    ctk.CTkButton(
        col, text="🔒  CIFRAR",
        font=ctk.CTkFont(size=F_MEDIUM, weight="bold"),
        fg_color=ACCENT_GREEN, hover_color="#1a6e2a",
        height=40, corner_radius=8,
        command=cifrar_mensagem
    ).pack(fill="x", pady=(0, 10))

    # ── Etapas intermediárias ──────────────────────────────────────────────

    create_divider(col)

    create_step_label(col,
        "① Mensagem convertida para números  (a=10, b=11 … z=35, espaço=99)",
        FG_YELLOW)
    enc_out_numeros = create_textbox(col, height=55, ro=True, text_color=FG_YELLOW)
    enc_out_numeros.pack(fill="x", pady=(0, 2))

    create_divider(col)

    create_step_label(col,
        "② Sequência quebrada em blocos  M < n",
        FG_ORANGE)
    enc_out_blocos = create_textbox(col, height=55, ro=True, text_color=FG_ORANGE)
    enc_out_blocos.pack(fill="x", pady=(0, 2))

    create_divider(col)

    create_step_label(col,
        "③ Blocos cifrados  C = Mᵉ mod n",
        FG_GREEN)
    enc_out_cifrado = create_textbox(col, height=60, ro=True, text_color=FG_GREEN)
    enc_out_cifrado.pack(fill="x")


# ── Coluna 2: Decifrar Mensagem ───────────────────────────────────────────────

def build_decrypt_col(parent):
    global dec_privkey, dec_cipher
    global dec_out_blocos_q, dec_out_blocos_dec, dec_out_texto

    col = create_scrollable_panel(parent, grid_col=2, padx=(5, 14))
    create_section_title(col, "🔓  Decifrar Mensagem", FG_CYAN)

    # ── Chave privada com botão de visibilidade ───────────────────────────
    row_dec_priv = ctk.CTkFrame(col, fg_color="transparent")
    row_dec_priv.pack(fill="x", pady=(0, 2))

    ctk.CTkLabel(row_dec_priv, text="Sua chave privada  (d, n)",
                 font=ctk.CTkFont(size=F_SMALL),
                 text_color=FG_GRAY, anchor="w").pack(side="left")

    btn_priv_decrypt = ctk.CTkButton(
        row_dec_priv, text="🙈",
        width=34, height=26, corner_radius=6,
        font=ctk.CTkFont(size=14),
        fg_color=ACCENT_GRAY, hover_color="#4a4f57",
        command=lambda: toggle_priv_decrypt(btn_priv_decrypt)
    )
    btn_priv_decrypt.pack(side="right")

    dec_privkey = create_entry(col, "ex: 2753, 3233")
    dec_privkey.pack(fill="x", pady=(0, 8))
    # ─────────────────────────────────────────────────────────────────────

    create_field_label(col, "Blocos cifrados recebidos  (números separados por espaço)")
    dec_cipher = create_textbox(col, height=100)
    dec_cipher.pack(fill="x", pady=(0, 10))

    ctk.CTkButton(
        col, text="🔓  DECIFRAR",
        font=ctk.CTkFont(size=F_MEDIUM, weight="bold"),
        fg_color=ACCENT_GRAY, hover_color="#3a3f47",
        height=40, corner_radius=8,
        command=decifrar_mensagem
    ).pack(fill="x", pady=(0, 10))

    create_divider(col)

    create_step_label(col, "① Blocos cifrados  C  recebidos", FG_ORANGE)
    dec_out_blocos_q = create_textbox(col, height=55, ro=True, text_color=FG_ORANGE)
    dec_out_blocos_q.pack(fill="x", pady=(0, 2))

    create_divider(col)

    create_step_label(col, "② Blocos decifrados  M = Cᵈ mod n", FG_YELLOW)
    dec_out_blocos_dec = create_textbox(col, height=55, ro=True, text_color=FG_YELLOW)
    dec_out_blocos_dec.pack(fill="x", pady=(0, 2))

    create_divider(col)

    create_step_label(col, "③ Mensagem recuperada", FG_CYAN)
    dec_out_texto = create_textbox(col, height=60, ro=True, text_color=FG_CYAN)
    dec_out_texto.pack(fill="x")


# ── Barra de status ───────────────────────────────────────────────────────────

def build_status_bar(parent):
    global status_lbl, status_tag

    bar = ctk.CTkFrame(parent, fg_color=BG_PANEL, height=44,
                       corner_radius=0, border_width=1, border_color=BORDER_COLOR)
    bar.grid(row=2, column=0, sticky="ew")
    bar.grid_columnconfigure(1, weight=1)   # empurra tudo à direita
    bar.grid_propagate(False)

    # col 0 — mensagem de status
    status_lbl = ctk.CTkLabel(
        bar, text="  Calculadora RSA pronta.  ",
        font=ctk.CTkFont(size=F_STATUS), text_color=FG_GRAY)
    status_lbl.grid(row=0, column=0, padx=(10, 0), pady=6)

    # col 1 — tag OK / Erro (expansível, ocupa o espaço do meio)
    status_tag = ctk.CTkLabel(
        bar, text=" ✔ Conectado ",
        font=ctk.CTkFont(size=F_STATUS, weight="bold"),
        text_color=FG_GREEN)
    status_tag.grid(row=0, column=1, sticky="w")

    # col 2 — versão
    ctk.CTkLabel(bar, text="Software v1.3.0  ",
                 font=ctk.CTkFont(size=F_STATUS), text_color=FG_GRAY
                 ).grid(row=0, column=2, padx=(0, 6), pady=6)

    # col 3 — botão Limpar (fixo na borda direita)
    ctk.CTkButton(
        bar, text="🗑  Limpar Tudo",
        font=ctk.CTkFont(size=F_STATUS, weight="bold"),
        fg_color="#6e2222", hover_color="#8f2d2d",
        corner_radius=6, height=28, width=148,
        command=limpar_tudo
    ).grid(row=0, column=3, padx=(0, 12), pady=6)


# ═════════════════════════════════════════════════════════════════════════════
# PONTO DE ENTRADA
# ═════════════════════════════════════════════════════════════════════════════

def build_app():
    app = ctk.CTk()
    app.title("Ferramenta RSA v1.3")
    app.geometry("1350x920")
    app.minsize(1100, 750)
    app.configure(fg_color=BG_MAIN)

    app.grid_columnconfigure(0, weight=1)
    app.grid_rowconfigure(0, weight=0)   # cabeçalho
    app.grid_rowconfigure(1, weight=1)   # colunas
    app.grid_rowconfigure(2, weight=0)   # status

    build_header(app)

    cols_frame = ctk.CTkFrame(app, fg_color="transparent")
    cols_frame.grid(row=1, column=0, sticky="nsew")
    cols_frame.grid_columnconfigure(0, weight=2)   # keygen   — estreita
    cols_frame.grid_columnconfigure(1, weight=3)   # cifrar   — larga
    cols_frame.grid_columnconfigure(2, weight=3)   # decifrar — larga
    cols_frame.grid_rowconfigure(0, weight=1)

    build_keygen_col(cols_frame)
    build_encrypt_col(cols_frame)
    build_decrypt_col(cols_frame)
    build_status_bar(app)

    return app


if __name__ == "__main__":
    app_window = build_app()
    app_window.mainloop()