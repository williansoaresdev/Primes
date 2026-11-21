"""
Miller-Rabin + mini-RSA (versão didática).

O que este arquivo faz:
  1. Implementa o teste de primalidade de Miller-Rabin.
  2. Usa esse teste para gerar dois primos grandes (p e q).
  3. Monta um par de chaves RSA e criptografa/descriptografa um texto.

ATENÇÃO: isto é material de ESTUDO. Um RSA de verdade usa "padding"
(OAEP) e bibliotecas auditadas. Nunca use este código para proteger
dados reais.

Como executar:
    python miller_rabin_rsa.py
Requer Python 3.8 ou superior (usa pow(e, -1, phi)).
"""

import secrets  # sorteio seguro (o módulo "random" NÃO deve ser usado em criptografia)
from dataclasses import dataclass
from math import gcd

# Primos pequenos usados como "peneira" antes do Miller-Rabin:
# descartar múltiplos deles é barato e elimina a maior parte dos candidatos.
PRIMOS_PEQUENOS = [
    2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
    53, 59, 61, 67, 71, 73, 79, 83, 89, 97,
]


# --------------------------------------------------------------------------
# 1) Teste de Miller-Rabin
# --------------------------------------------------------------------------
def decompor(n: int) -> tuple[int, int]:
    """Escreve n - 1 como 2^s * d, com d ímpar, e devolve (s, d).

    Exemplo: n = 341 -> n - 1 = 340 = 2^2 * 85  ->  devolve (2, 85).
    """
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    return s, d


def miller_rabin(n: int, rodadas: int = 40) -> bool:
    """Diz se n é 'provavelmente primo' (True) ou 'certamente composto' (False).

    Cada rodada usa uma base 'a' aleatória. Se o número for composto,
    cada rodada o desmascara com chance de pelo menos 75%. Com 40 rodadas
    a chance de erro é menor que 1 em 10^24.
    """
    if n < 2:
        return False

    # Peneira rápida com primos pequenos.
    for p in PRIMOS_PEQUENOS:
        if n == p:
            return True
        if n % p == 0:
            return False

    s, d = decompor(n)

    for _ in range(rodadas):
        a = secrets.randbelow(n - 3) + 2  # base aleatória no intervalo [2, n-2]
        x = pow(a, d, n)                  # a^d mod n (exponenciação modular)

        if x == 1 or x == n - 1:
            continue  # passou nesta rodada

        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break  # passou nesta rodada
        else:
            # Nunca chegou em n-1: achamos uma prova de que n é composto.
            return False

    return True


def miller_rabin_passo_a_passo(n: int, a: int) -> None:
    """Mostra na tela cada passo do Miller-Rabin para UMA base 'a'.

    Serve só para aprender: não sorteia nada, você escolhe a base.
    """
    s, d = decompor(n)
    print(f"\nTestando n = {n} com a base a = {a}")
    print(f"  n - 1 = {n - 1} = 2^{s} * {d}")

    x = pow(a, d, n)
    print(f"  x = a^d mod n = {a}^{d} mod {n} = {x}")
    if x == 1 or x == n - 1:
        print("  x é 1 ou n-1  ->  passou nesta rodada (n pode ser primo)")
        return

    for i in range(1, s):
        x_antigo = x
        x = pow(x, 2, n)
        print(f"  elevando ao quadrado: {x_antigo}^2 mod {n} = {x}")
        if x == n - 1:
            print("  chegou em n-1  ->  passou nesta rodada (n pode ser primo)")
            return
        if x == 1:
            print(f"  {x_antigo} NÃO é 1 nem n-1, mas o quadrado dele é 1!")
            break

    print("  Resultado: n é COMPOSTO (certeza absoluta).")


# --------------------------------------------------------------------------
# 2) Geração de primos grandes
# --------------------------------------------------------------------------
def gerar_primo(bits: int) -> int:
    """Gera um primo aleatório com exatamente 'bits' bits."""
    if bits < 16:
        raise ValueError("Use pelo menos 16 bits.")

    while True:
        candidato = secrets.randbits(bits)
        # Força os dois bits mais altos a 1 (garante o tamanho: p*q terá
        # exatamente 2*bits bits) e o bit mais baixo a 1 (número ímpar).
        candidato |= (1 << (bits - 1)) | (1 << (bits - 2)) | 1
        if miller_rabin(candidato):
            return candidato


# --------------------------------------------------------------------------
# 3) Mini-RSA
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class ChaveRSA:
    """Guarda os números de uma chave RSA.

    Pública  = (n, e)  -> pode ser divulgada.
    Privada  = (n, d)  -> deve ficar em segredo (p e q também!).
    """
    n: int
    e: int
    d: int
    p: int
    q: int


def gerar_chaves(bits_primo: int = 512, e: int = 65537) -> ChaveRSA:
    """Gera uma chave RSA com primos de 'bits_primo' bits cada.

    Com 512 bits por primo, n tem 1024 bits (suficiente para estudar,
    mas fraco para uso real, onde se usa 2048 bits ou mais).
    """
    while True:
        p = gerar_primo(bits_primo)
        q = gerar_primo(bits_primo)
        if p == q:
            continue

        phi = (p - 1) * (q - 1)
        # 'e' precisa ser coprimo de phi, senão não existe o inverso 'd'.
        if gcd(e, phi) != 1:
            continue

        d = pow(e, -1, phi)  # inverso modular: (e * d) mod phi = 1
        return ChaveRSA(n=p * q, e=e, d=d, p=p, q=q)


def texto_para_inteiro(texto: str) -> int:
    """Converte um texto em um número (bytes UTF-8 lidos como inteiro)."""
    return int.from_bytes(texto.encode("utf-8"), "big")


def inteiro_para_texto(numero: int) -> str:
    """Faz o caminho inverso de texto_para_inteiro."""
    tamanho = (numero.bit_length() + 7) // 8
    return numero.to_bytes(tamanho, "big").decode("utf-8")


def criptografar(mensagem: str, n: int, e: int) -> int:
    """c = m^e mod n"""
    m = texto_para_inteiro(mensagem)
    if m >= n:
        raise ValueError("Mensagem grande demais para esta chave.")
    return pow(m, e, n)


def descriptografar(cifrado: int, n: int, d: int) -> str:
    """m = c^d mod n"""
    m = pow(cifrado, d, n)
    return inteiro_para_texto(m)


# --------------------------------------------------------------------------
# Demonstração
# --------------------------------------------------------------------------
def main() -> None:
    print("=== 1) Miller-Rabin pegando o 341 (que enganava a fórmula de Fermat) ===")
    miller_rabin_passo_a_passo(341, 2)

    print("\n=== 2) Alguns números conhecidos ===")
    for n in (97, 341, 561, 1729, 7919, 2**61 - 1, 2**61 + 1):
        resultado = "provavelmente primo" if miller_rabin(n) else "composto"
        print(f"  {n}: {resultado}")

    print("\n=== 3) Gerando chaves RSA (primos de 512 bits)... ===")
    chave = gerar_chaves(bits_primo=512)
    print(f"  n tem {chave.n.bit_length()} bits")
    print(f"  e = {chave.e}")
    print(f"  p (início) = {str(chave.p)[:30]}...")
    print(f"  q (início) = {str(chave.q)[:30]}...")

    print("\n=== 4) Criptografando e descriptografando ===")
    mensagem = "Olá, RSA! Números primos são incríveis."
    cifrado = criptografar(mensagem, chave.n, chave.e)
    print(f"  Mensagem original : {mensagem}")
    print(f"  Cifrada (início)  : {str(cifrado)[:60]}...")
    print(f"  Descriptografada  : {descriptografar(cifrado, chave.n, chave.d)}")


if __name__ == "__main__":
    main()
