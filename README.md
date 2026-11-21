# Primes: números primos, Fermat, Miller-Rabin e mini-RSA

Projeto de estudo que nasceu de uma anotação de 2024: uma fórmula descoberta
"brincando" no Excel para reconhecer números primos. Aqui está a explicação
do que ela é, onde ela falha e como a matemática evoluiu dela até o RSA.

## 1. A fórmula original

```
((2^n) - 1) mod n = 1
```

Ela equivale a `2^n ≡ 2 (mod n)`, que é o **Pequeno Teorema de Fermat**
(1640) com base 2:

> Se `p` é primo, então `a^p ≡ a (mod p)` para qualquer inteiro `a`.

Ou seja, **todo número primo passa** na fórmula.

### O problema: a volta não vale

Alguns números **compostos** também passam. Eles são chamados de
**pseudoprimos de Fermat de base 2** (ou números de Poulet):

| n    | fatoração  |
|------|------------|
| 341  | 11 × 31    |
| 561  | 3 × 11 × 17 |
| 645  | 3 × 5 × 43 |
| 1105 | 5 × 13 × 17 |

Por isso a fórmula é um **teste probabilístico**:

- Se **reprova**, o número é composto, com certeza.
- Se **aprova**, ele é *provavelmente* primo.

Curiosidades:

- Existem pseudoprimos **pares**; os primeiros são 161038 e 215326.
- O número 1 não passa: `(2^1 - 1) mod 1 = 0`.
- Testar outras bases (3, 5, 7...) elimina quase todos os impostores, mas os
  **números de Carmichael** (561, 1105, 1729...) enganam todas as bases
  coprimas com eles.

### Por que o Excel travou

O Excel calcula `2^n` inteiro, e esse número cresce absurdamente rápido
(2^1000 já tem mais de 300 dígitos). A solução é a **exponenciação modular**:
aplicar o `mod` a cada multiplicação, de modo que o número nunca cresça.
Em Python isso é `pow(2, n, n)`.

## 2. Miller-Rabin: a versão melhorada

O teste de Miller-Rabin usa um fato extra: **se `n` é primo, os únicos
números cujo quadrado dá 1 (módulo `n`) são 1 e `n − 1`**. Se aparecer
qualquer outro, `n` é composto.

Para testar um `n` ímpar:

1. Escreva `n − 1 = 2^s × d`, com `d` ímpar.
2. Escolha uma base aleatória `a` entre 2 e `n − 2`.
3. Calcule `x = a^d mod n`.
4. Se `x` for 1 ou `n − 1`, passou nesta rodada.
5. Senão, eleve `x` ao quadrado até `s − 1` vezes; se virar `n − 1`, passou.
6. Se nunca virou `n − 1`, `n` é **composto, com certeza**.

**Exemplo com o 341 e a base 2:** `340 = 2² × 85`, então `2^85 mod 341 = 32`.
Elevando ao quadrado, `32² mod 341 = 1`. O 32 não é 1 nem 340, mas o quadrado
dele é 1, o que é impossível para um primo. Logo, 341 é composto. O teste de
Fermat não pegava esse caso; o Miller-Rabin pega.

**Confiabilidade:** para um composto, no máximo 1/4 das bases enganam o teste.
Com `k` rodadas, a chance de erro é no máximo `(1/4)^k`. Com 40 rodadas, menos
de 1 em 10^24.

## 3. Onde o RSA entra

O Miller-Rabin **não** é usado para criptografar nem para descriptografar.
Ele serve para **gerar a chave**, encontrando primos gigantes:

1. Sorteia-se um número ímpar com o tamanho desejado (ex.: 1024 bits).
2. Descartam-se os que têm fatores pequenos.
3. Aplica-se o Miller-Rabin; se reprovar, volta ao passo 1.

Perto de 2^1024, cerca de 1 a cada 700 números é primo, então poucas
centenas de tentativas bastam.

Com dois primos `p` e `q`, o RSA funciona assim:

- `n = p × q` (público)
- `phi = (p − 1) × (q − 1)`
- `e` = 65537 (público) e `d` = inverso de `e` módulo `phi` (privado)
- Criptografar: `c = m^e mod n`
- Descriptografar: `m = c^d mod n`

A segurança vem do fato de que, conhecendo só `n`, fatorar e descobrir
`p` e `q` é inviável quando eles são grandes.

## 4. Os programas

Requer **Python 3.8 ou superior**. Não precisa instalar nenhuma biblioteca.

### `pseudoprimos.py`

Testa a fórmula original até um limite e lista os compostos que passam.

```
python pseudoprimos.py            # testa até 1.000.000
python pseudoprimos.py 5000000    # testa até 5.000.000
```

Resultado até 1.000.000: 78.498 primos (todos passam, como Fermat garante) e
247 compostos que também passam, entre eles os pares 161038 e 215326.

### `miller_rabin_rsa.py`

Demonstração completa:

1. Mostra o Miller-Rabin passo a passo desmascarando o 341.
2. Testa alguns números conhecidos (97, 561, 1729, 7919...).
3. Gera dois primos de 512 bits e monta uma chave RSA de 1024 bits.
4. Criptografa e descriptografa um texto.

```
python miller_rabin_rsa.py
```

Funções principais, para quem quiser ler o código:

| Função | O que faz |
|--------|-----------|
| `decompor(n)` | Escreve `n − 1` como `2^s × d` |
| `miller_rabin(n, rodadas)` | Diz se `n` é provavelmente primo |
| `miller_rabin_passo_a_passo(n, a)` | Mostra cada passo na tela (didático) |
| `gerar_primo(bits)` | Sorteia candidatos até achar um primo |
| `gerar_chaves(bits_primo)` | Monta uma chave RSA (`ChaveRSA`) |
| `criptografar` / `descriptografar` | Aplicam `m^e mod n` e `c^d mod n` |

## 5. Aviso importante

O RSA deste projeto é **apenas educativo**. Falta o *padding* (OAEP) e as
chaves são pequenas. **Nunca use este código para proteger dados reais**;
em sistemas de verdade, use bibliotecas criptográficas auditadas.

## 6. Para continuar estudando

- Adicionar o teste de Fermat com outras bases (3, 5, 7...) e ver os impostores sumirem.
- Contar os números de Carmichael encontrados em `pseudoprimos.py`.
- Comparar o tempo do Miller-Rabin com a divisão por tentativa para números grandes.
- Ler sobre o teste AKS (2002), o primeiro algoritmo determinístico de tempo polinomial para primalidade.
