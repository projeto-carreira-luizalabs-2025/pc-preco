# pc-preco

## 📌 O que é este projeto?

O `pc-preco` é um microsserviço responsável por gerenciar e expor as **informações de preço** dos produtos vendidos por
varejistas no marketplace.

Esse serviço tem como função principal fornecer os valores exibidos ao consumidor final, considerando diferentes
condições de pagamento, como:

- Preço à vista (com ou sem desconto)
- Preço a prazo (com ou sem juros)
- Variações por vendedor (mesmo produto, diferentes preços)

Ele se integra diretamente com os microsserviços de:

- `pc-catalogo`: para identificar a qual produto o preço se refere.
- `pc-identidade`: para saber qual varejista está ofertando o preço.

Além disso, o `pc-preco` atua em conjunto com:

- `pc-estoque`: para que o preço exibido esteja alinhado à disponibilidade do produto.
- `pc-frete`: que junto ao preço, compõe o custo final percebido pelo consumidor.

Cada microsserviço mantém responsabilidades bem definidas, mas trabalham de forma integrada para oferecer uma
experiência de compra completa.

---

## 👥 Participantes

- Carlos Eduardo
- Eduardo Ribeiro
- João Lucas Ferreira
- Layza Nauane De Paula Silva

---

## 📁 Estrutura do projeto

```bash
.
├── README.md               # Descrição do serviço
├── devtools/
│   └── info-projeto.md     # Documento de levantamento da informação base
└── src/                    # Código-fonte da aplicação (em construção)
