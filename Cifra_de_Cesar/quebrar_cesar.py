import re


def carregar_dicionario(nome_arquivo):
    with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
        return {
            linha.strip().lower()
            for linha in arquivo
            if linha.strip()
        }


def descriptografar_cesar(texto, deslocamento):

    resultado = ""

    for caractere in texto:

        if caractere.isalpha():

            if caractere.isupper():
                inicio = ord('A')
            else:
                inicio = ord('a')

            nova_letra = chr(
                (ord(caractere) - inicio - deslocamento) % 26
                + inicio
            )

            resultado += nova_letra

        else:
            resultado += caractere

    return resultado


def extrair_palavras(texto):
    return re.findall(
        r'\b[a-zA-ZÀ-ÿ]+\b',
        texto.lower()
    )


def calcular_pontuacao(texto, dicionario):

    palavras = extrair_palavras(texto)

    if len(palavras) == 0:
        return 0

    acertos = sum(
        1 for palavra in palavras
        if palavra in dicionario
    )

    return acertos


def quebrar_cifra(texto_cifrado, dicionario):

    resultados = []

    for deslocamento in range(26):

        tentativa = descriptografar_cesar(
            texto_cifrado,
            deslocamento
        )

        pontuacao = calcular_pontuacao(
            tentativa,
            dicionario
        )

        resultados.append(
            (
                deslocamento,
                pontuacao,
                tentativa
            )
        )

    resultados.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return resultados


# ----------------------
# Programa principal
# ----------------------

dicionario = carregar_dicionario(
    "dicionario.txt"
)

texto = input(
    "Digite a mensagem cifrada:\n"
)

resultados = quebrar_cifra(
    texto,
    dicionario
)

print("\n=== MELHORES RESULTADOS ===\n")

for deslocamento, pontos, texto in resultados[:5]:

    print(f"Chave: {deslocamento}")
    print(f"Palavras reconhecidas: {pontos}")
    print(texto)
    print("-" * 60)
    #print(resultados)