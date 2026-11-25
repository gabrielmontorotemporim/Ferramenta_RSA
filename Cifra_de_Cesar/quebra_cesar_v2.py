import re
import customtkinter as ctk
from tkinter import messagebox


# ----------------------
# Lógica da cifra
# ----------------------

def carregar_dicionario(nome_arquivo: str) -> set[str]:
    with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
        return {
            linha.strip().lower()
            for linha in arquivo
            if linha.strip()
        }


def descriptografar_cesar(texto: str, deslocamento: int) -> str:
    resultado = ""
    for caractere in texto:
        if caractere.isalpha():
            inicio = ord('A') if caractere.isupper() else ord('a')
            nova_letra = chr(
                (ord(caractere) - inicio - deslocamento) % 26 + inicio
            )
            resultado += nova_letra
        else:
            resultado += caractere
    return resultado


def extrair_palavras(texto: str) -> list[str]:
    return re.findall(r'\b[a-zA-ZÀ-ÿ]+\b', texto.lower())


def calcular_pontuacao(texto: str, dicionario: set[str]) -> int:
    palavras = extrair_palavras(texto)
    if not palavras:
        return 0
    return sum(1 for palavra in palavras if palavra in dicionario)


def quebrar_cifra(texto_cifrado: str, dicionario: set[str]) -> tuple[int, str] | None:
    total_palavras = len(extrair_palavras(texto_cifrado))
    if total_palavras == 0:
        return None

    for deslocamento in range(26):
        tentativa = descriptografar_cesar(texto_cifrado, deslocamento)
        pontuacao = calcular_pontuacao(tentativa, dicionario)
        if pontuacao == total_palavras:
            return deslocamento, tentativa

    return None


# ----------------------
# Interface gráfica
# ----------------------

class App(ctk.CTk):

    DICIONARIO_PATH = "dicionario.txt"

    def __init__(self):
        super().__init__()

        self.title("Quebrador de Cifra de César")
        self.geometry("620x480")
        self.resizable(False, False)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        try:
            self.dicionario = carregar_dicionario(self.DICIONARIO_PATH)
        except FileNotFoundError:
            messagebox.showerror(
                "Erro",
                f"Arquivo '{self.DICIONARIO_PATH}' não encontrado.\n"
                "Coloque o dicionário na mesma pasta do script."
            )
            self.destroy()
            return

        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # --- Título ---
        ctk.CTkLabel(
            self,
            text="Quebrador da Cifra de César",
            font=ctk.CTkFont(size=24, weight="bold"),
        ).grid(row=0, column=0, padx=24, pady=(24, 8), sticky="w")

        # --- Campo de entrada ---
        ctk.CTkLabel(
            self,
            text="Mensagem cifrada:",
            font=ctk.CTkFont(size=20),
        ).grid(row=1, column=0, padx=24, pady=(0, 4), sticky="sw")

        self.entrada = ctk.CTkTextbox(
            self,
            height=130,
            font=ctk.CTkFont(family="Courier New", size=20),
            wrap="word",
        )
        self.entrada.grid(row=2, column=0, padx=24, sticky="ew")

        # --- Botões ---
        frame_botoes = ctk.CTkFrame(self, fg_color="transparent")
        frame_botoes.grid(row=3, column=0, padx=24, pady=12, sticky="ew")
        frame_botoes.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            frame_botoes,
            text="🔓  Decifrar",
            font=ctk.CTkFont(size=20, weight="bold"),
            height=40,
            command=self._decifrar,
        ).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        ctk.CTkButton(
            frame_botoes,
            text="🗑  Limpar",
            font=ctk.CTkFont(size=20),
            height=40,
            fg_color="gray30",
            hover_color="gray20",
            command=self._limpar,
        ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

        # --- Resultado ---
        ctk.CTkLabel(
            self,
            text="Resultado:",
            font=ctk.CTkFont(size=20),
        ).grid(row=4, column=0, padx=24, pady=(0, 4), sticky="sw")

        frame_resultado = ctk.CTkFrame(self)
        frame_resultado.grid(row=5, column=0, padx=24, pady=(0, 8), sticky="ew")
        frame_resultado.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            frame_resultado,
            text="Chave:",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=0, column=0, padx=(16, 8), pady=10)

        self.label_chave = ctk.CTkLabel(
            frame_resultado,
            text="—",
            font=ctk.CTkFont(family="Courier New", size=20),
        )
        self.label_chave.grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            frame_resultado,
            text="Mensagem:",
            font=ctk.CTkFont(size=20, weight="bold"),
        ).grid(row=1, column=0, padx=(16, 8), pady=(0, 10), sticky="n")

        self.label_mensagem = ctk.CTkLabel(
            frame_resultado,
            text="—",
            font=ctk.CTkFont(family="Courier New", size=20),
            wraplength=460,
            justify="left",
            anchor="w",
        )
        self.label_mensagem.grid(row=1, column=1, pady=(0, 10), sticky="w")

    def _decifrar(self):
        texto = self.entrada.get("1.0", "end").strip()

        if not texto:
            messagebox.showwarning("Atenção", "Digite uma mensagem cifrada.")
            return

        resultado = quebrar_cifra(texto, self.dicionario)

        if resultado:
            deslocamento, mensagem = resultado
            self.label_chave.configure(text=str(deslocamento))
            self.label_mensagem.configure(text=mensagem)
        else:
            self.label_chave.configure(text="—")
            self.label_mensagem.configure(
                text="Não foi possível decifrar.\nVerifique o dicionário."
            )

    def _limpar(self):
        self.entrada.delete("1.0", "end")
        self.label_chave.configure(text="—")
        self.label_mensagem.configure(text="—")


if __name__ == "__main__":
    app = App()
    app.mainloop()