"""
Testa a fórmula do Willian: ((2^n) - 1) mod n = 1

Procura números que PASSAM na fórmula mas NÃO são primos
(os chamados pseudoprimos de Fermat de base 2).

Como executar:
    python pseudoprimos.py              (testa até 1.000.000)
    python pseudoprimos.py 5000000      (testa até 5.000.000)
"""

import sys


def crivo_de_eratostenes(limite: int) -> list[bool]:
    """Devolve uma lista onde e_primo[n] é True se n for primo (n <= limite)."""
    e_primo = [True] * (limite + 1)
    e_primo[0] = e_primo[1] = False
    i = 2
    while i * i <= limite:
        if e_primo[i]:
            for multiplo in range(i * i, limite + 1, i):
                e_primo[multiplo] = False
        i += 1
    return e_primo


def passa_na_formula(n: int) -> bool:
    """Implementa ((2^n) - 1) mod n = 1 sem calcular o 2^n gigante.

    pow(2, n, n) calcula 2^n mod n fazendo o 'mod' a cada multiplicação,
    então os números nunca crescem (é isso que o Excel não consegue fazer).
    """
    return (pow(2, n, n) - 1) % n == 1


def main() -> None:
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 1_000_000
    e_primo = crivo_de_eratostenes(limite)

    quantidade_primos = 0
    impostores = []  # passam na fórmula, mas são compostos

    for n in range(2, limite + 1):
        passou = passa_na_formula(n)
        if e_primo[n]:
            quantidade_primos += 1
            # Fermat garante: todo primo TEM que passar. Se falhar, há bug.
            assert passou, f"Erro: o primo {n} não passou!"
        elif passou:
            impostores.append(n)

    print(f"Números testados: 2 até {limite:,}")
    print(f"Primos encontrados: {quantidade_primos:,} (todos passaram na fórmula)")
    print(f"Compostos que passaram (impostores): {len(impostores)}")
    print("\nOs primeiros impostores:")
    for n in impostores[:15]:
        print(f"  {n}")

    pares = [n for n in impostores if n % 2 == 0]
    if pares:
        print(f"\nImpostores PARES (raros!): {pares}")


if __name__ == "__main__":
    main()
