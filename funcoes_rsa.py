# Teste de primalidade
def e_primo(n):
    # Se n < 2, não é primo (0 e 1 não são primos)
    if n < 2:
        return False

    # Se n é 2 ou 3, é primo
    if n < 4:
        return True

    # Se o número for par (e maior que 2), não é primo
    if n % 2 == 0:
        return False

    # Testamos apenas os ímpares de 3 até a raiz quadrada de n
    # (i * i <= n é o mesmo que i <= raiz de n)
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i = i + 2

    # Se nenhum divisor foi encontrado, o número é primo
    return True

# Encontra o MDC e os coeficientes de Bezout
def inverso_modular_estendido(a, m):
    m0, y, x = m, 0, 1
    if m == 1:
        return 0
    while a > 1:
        # q é o quociente
        q = a // m
        t = m
        # m é o resto, processar da mesma forma que o algoritmo de Euclides
        m = a % m
        a = t
        t = y
        # Atualizar x e y
        y = x - q * y
        x = t
    # Tornar x positivo
    if x < 0:
        x = x + m0
    return x

#Cálculo do MDC (Algoritmo de Euclides)
def calcular_mdc(a, b):
    while b != 0:
        a, b = b, a % b
    return a

#Encontra o menor coprimo ímpar com phi
def gerar_expoente_publico(phi):
    # Começamos com e = 3, pois e deve ser ímpar e > 1
    e = 3
    while e < phi:
        if calcular_mdc(e, phi) == 1:
            return e
        e += 2  # Testamos apenas os ímpares para ser mais rápido
    return None

def transformar_em_numeros(mensagem):
    # Definimos o alfabeto para referência
    alfabeto = "abcdefghijklmnopqrstuvwxyz"

    # Criamos o mapeamento: a=11, b=12, c=13...
    mapeamento = {letra: str(i + 10) for i, letra in enumerate(alfabeto)}

    # Adicionamos a regra especial para o espaço
    mapeamento[' '] = '99'

    resultado = []

    # Convertemos a mensagem para minúsculas para evitar erros
    for caractere in mensagem.lower():
        if caractere in mapeamento:
            resultado.append(mapeamento[caractere])
        else:
            # Caso haja algum caractere que não definimos (ex: ponto final)
            resultado.append('??')
            return "erro"

    return "".join(resultado)


def quebrar_em_blocos(sequencia, n_maximo):
    dados = str(sequencia).replace(" ", "")
    blocos = []
    i = 0

    while i < len(dados):
        # Começamos com 1 dígito
        j = i + 1

        # Tentamos expandir o bloco o máximo possível
        while j < len(dados):
            proximo_bloco_com_mais_um = dados[i : j + 1]
            valor = int(proximo_bloco_com_mais_um)

            # 1. Se adicionar o próximo dígito estourar o limite, paramos aqui
            if valor > n_maximo:
                break

            # 2. Se o dígito APÓS este que estamos testando for '0',
            # nós SOMOS OBRIGADOS a incluir o próximo dígito neste bloco
            # para que o próximo bloco não comece com zero.
            if j + 1 < len(dados) and dados[j + 1] == '0':
                # Mas só incluímos se isso não estourar o n_maximo
                if int(dados[i : j + 2]) <= n_maximo:
                    j += 1 # Avança para absorver o dígito que precede o zero
                else:
                    # Se estourar, temos um problema matemático de design:
                    # n_maximo é pequeno demais para evitar o zero.
                    break

            j += 1

        blocos.append(dados[i:j])
        i = j

    return blocos

def codificar_blocos(lista_blocos, e, n):
    blocos_codificados = []

    for bloco in lista_blocos:
        # Converte o bloco (string) em inteiro (M)
        cod_M = int(bloco)

        # Aplica a fórmula: (M^e) % n
        cod_C = pow(cod_M, e, n)

        blocos_codificados.append(cod_C)

    return blocos_codificados

def decodificar_blocos(lista_codificada, d, n):
    blocos_decodificados = []

    for bloco_c in lista_codificada:
        # Aplica a fórmula RSA inversa: (C^d) % n
        valor_m = pow(bloco_c, d, n)

        # Converte de volta para string para podermos remontar a mensagem
        blocos_decodificados.append(str(valor_m))

    return blocos_decodificados

def transformar_em_texto(sequencia_numerica):
    # Recriamos o alfabeto para reconstruir o mapeamento
    alfabeto = "abcdefghijklmnopqrstuvwxyz"

    # Criamos o mapeamento inverso: '10': 'a', '11': 'b'...
    mapeamento_reverso = {str(i + 10): letra for i, letra in enumerate(alfabeto)}

    # Adicionamos o espaço
    mapeamento_reverso['99'] = ' '

    resultado_texto = []

    # Percorremos a string pulando de 2 em 2
    for i in range(0, len(sequencia_numerica), 2):
        par = sequencia_numerica[i:i+2]

        if par in mapeamento_reverso:
            resultado_texto.append(mapeamento_reverso[par])
        else:
            resultado_texto.append('?') # Para caracteres desconhecidos

    return "".join(resultado_texto)