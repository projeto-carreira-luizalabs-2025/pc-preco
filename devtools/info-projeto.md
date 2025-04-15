### Definição do preço

O preço do produto irá ser representado de várias foras, de acordo com a forma de pagamento, números de parcelas e valor do frete. Dependendo dessas variáveis,
o cálculo do preço pode ser diferente.

### Múltiplas formas de pagamento

- Cartão da loja: O preço total pode sofrer desconto e pode ter várias parcelas.
- Cartão de crédito: O preço pode ser à vista sem desconto ou pode ter várias parcelas.
- Pix: Preço total pode sofrer desconto e não há parcelas.
- Boleto: Preço é à vista sem desconto e não há parcelas.

### Parcelas

Dependendo da forma de pagamento, o preço poderá ser dividido em parcelas. Pode ser definido o número limite de parcelas e se haverá jutos a partir de X parcelas.

#### Exemplo

- Dividido em até 10 parcelas, não haverá juros.
- De 11 a 12 parcelas, haverá juros

### Juros de parcelas

O juros da parcela são calculados de acordo com a fórmula (Tabela Price):

$$
P = \frac{V \cdot i}{1 - (1 + i)^{-n}}
$$

#### Exemplo:

Preço à vista: R$ 1.000,00
Parcelado em: 12x
Juros: 2,5% ao mês

$$
P = \frac{1000 \cdot 0{,}025}{1 - (1 + 0{,}025)^{-12}}
$$

Valor aproximado da parcela: **R\$96,22** 

Preço novo: 

$$
12 \cdot 96{,}22 = R\$1.154,64
$$

### Preço total + Frete

O preço total pode ser representado já com o valor do frete acrecentado.

O valor do frete será calculado em "pc-frete"



