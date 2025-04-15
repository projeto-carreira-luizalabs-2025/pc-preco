### Definição do preço

O preço do produto irá ser representado de várias formas. O cálculo será diferente de acordo com a forma de pagamento, números de parcelas ou valor do frete.

### Múltiplas formas de pagamento

O preço pode mudar de acordo com a forma de pagamento que o cliente escolher:

- Cartão da loja: O preço total pode sofrer desconto e pode ter várias parcelas.
- Cartão de crédito: O preço pode ser à vista sem desconto ou pode ter várias parcelas.
- Pix: Preço total pode sofrer desconto e não há parcelas.
- Boleto: Preço é à vista sem desconto e não há parcelas.

### Parcelas

- Dependendo da forma de pagamento, o preço poderá ser dividido em parcelas. Cada parcela representa o preço total dividido pelo total de parcelas.
- O preço total e preço das parcelas poderão mudar caso a partir de X parcelas houver acrécimo de juros.

#### Exemplo

- Dividido em até 10 parcelas, não haverá juros.
- De 11 a 12 parcelas, haverá juros.

### Juros de parcelas

O valor novo das parcelas é calculado de acordo com a fórmula (Tabela Price):

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

O valor do frete será calculado em "pc-frete".



