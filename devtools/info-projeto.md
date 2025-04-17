# 💸 Precificação do produto 

Esse documento tem como finalidade determinar como o preço será representado no projeto.

## 💰 Preço Percebido pelo Cliente

O preço do produto para o cliente irá ser representado de várias formas. O cálculo será diferente de acordo com a forma de pagamento, número de parcelas ou valor do frete.

### 💳 Múltiplas formas de pagamento

O preço pode mudar de acordo com a forma de pagamento que o cliente escolher:

- Cartão da loja: O preço total pode sofrer desconto e pode ter várias parcelas.
- Cartão de crédito: O preço pode ser à vista sem desconto ou pode ter várias parcelas.
- Pix: Preço total pode sofrer desconto e não há parcelas.
- Boleto: Preço é à vista sem desconto e não há parcelas.

---

### Parcelas

- Dependendo da forma de pagamento, o preço poderá ser dividido em parcelas. Cada parcela representa o preço total dividido pelo total de parcelas.
- O preço total e o preço das parcelas poderão mudar caso, a partir de X parcelas, houver acréscimo de juros.

#### 📌 Exemplo

- Dividido em até 10 parcelas, não haverá juros.
- De 11 a 12 parcelas, haverá juros.

---

### Juros de parcelas

O novo valor das parcelas pode ser calculado por fórmulas específicas, um exemplo usando Tabela Price:

$$
P = \frac{V \cdot i}{1 - (1 + i)^{-n}}
$$

#### 📌 Exemplo

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

---

### Preço total + Frete

O preço total pode ser representado já com o valor do frete acrescentado.

O valor do frete será calculado em "pc-frete".

---

### Frete Grátis por Valor de Compra

O frete grátis poderá ser aplicado automaticamente sob as seguintes circunstâncias:

- Frete grátis para pedidos com o valor total igual ou superior a R$ 100,00.

- O valor considerado é o total dos produtos no carrinho, sem incluir o frete.

📌 Exemplo

Carrinho com R$ 99,90 em produtos → Frete será cobrado normalmente.

Carrinho com R$ 100,00 ou mais em produtos → Frete grátis será automaticamente aplicado.

<br>

## 💰 Definição do preço percebido pelo vendedor

### Custo total do produto

Será o custo total para a venda do produto, poderá ser influenciado por taxas, como comissão da plataforma, impostos, taxas de logística, etc.

### Margem de lucro do vendedor

Será o valor que o vendedor irá lucrar após os custos aplicados na venda de seu produto.

<br>

## 🎯 Regras para precificação

O preço do produto deverá seguir regras para evitar preços abusivos, refletir datas promocionais, limitações impostas pelo fabricante do produto, etc.  

---

### Margens

- Margem mínima: 20% sobre o custo
- Margem máxima: 80% sobre o custo

#### 📌 Exemplo

Custo: R$ 1.000 → Preço permitido: de R$ 1.200 a R$ 1.800

---

### Preço mínimo sugerido

- Preço mínimo sugerido pelo fabricante (MSRP)

---

### Preço por Estoque

#### 📌 Exemplo

- Caso produto estiver mais de 30 dias no estoque → 10% de desconto
- Caso produto estiver mais de 60 dias no estoque → 20% de desconto

---

### Preço promocional em datas especiais

#### 📌 Exemplo

- Caso estiver na Black Friday → mínimo 15% de desconto
- Caso estivar na Semana do Consumidor → frete grátis ou desconto progressivo

---

### Preço por reputação do vendedor

Vendedores com boa reputação podem cobrar mais.

#### 📌 Exemplo

- Se reputação for 5 estrelas e índice de devolução < 3%, o vendedor pode ultrapassar o preço médio em até 10%.

---

### ⚠️  Observação: 

Este documento está em fase de pesquisa e planejamento inicial. Os critérios e regras descritos podem sofrer ajustes conforme novas necessidades surjam ou conforme o projeto evoluir. Sugestões e contribuições são bem-vindas.