# 💸 Microsserviço de Preço (`pc-preco`) - Conceito, Regras e Integrações

*(Data da Versão: 17 de Abril de 2025)*

## 1. Olá, Time! Qual o objetivo deste documento? 🤔

Bem-vindos ao guia oficial do nosso microsserviço `pc-preco`! Este documento é a nossa fonte central para entender tudo sobre ele: o que ele faz, quais informações gerencia, suas regras de negócio e como ele se encaixa no grande quebra-cabeça do nosso marketplace. Queremos que seja claro tanto para quem está começando quanto para quem já tem mais experiência! 😊

Lembrando, nosso sistema usa **microsserviços**, que são como peças de LEGO, cada uma com sua função especializada:

* `pc-catalogo`: O "catálogo" dos nossos produtos.
* `pc-estoque`: O "controlador" da quantidade de produtos.
* `pc-frete`: O "calculador" dos custos de entrega.
* `pc-identidade`: O "guardião" das informações dos vendedores.
* **`pc-preco` (É nóis! 🎉):** O "cérebro" por trás dos preços que aparecem na loja.

Aqui vamos detalhar:

* O conceito de "Registro de Preço".
* Como diferentes tipos de preço funcionam na prática.
* Os cálculos que o `pc-preco` realiza (incluindo fórmulas!).
* As regras de negócio importantes e por que elas existem (fundamentadas em nossa pesquisa de mercado!).
* O que o `pc-preco` faz e o que ele NÃO faz (suas responsabilidades).
* Como ele "conversa" com os outros microsserviços usando **APIs** (Application Programming Interfaces - uma forma padronizada de sistemas conversarem entre si).
* Nossas referências e conclusões do **Benchmarking** (análise de concorrentes).

## 2. O Conceito Central: O Registro de Preço 💰🏷️

A peça fundamental que o `pc-preco` gerencia é o **Registro de Preço**. Pense nele como uma "ficha" completa que define o valor e as condições de venda para um **produto específico** (identificado pelo seu `productId`, originado no `pc-catalogo`) oferecido por um **vendedor específico** (identificado pelo `sellerId`, originado no `pc-identidade`).

É super importante saber que um mesmo produto pode ter vários Registros de Preço diferentes (vendedores diferentes, promoções com datas de validade, etc.). O `pc-preco` armazena todos esses registros e fornece a lógica para determinar qual preço é o mais relevante para o cliente em um dado momento. Ele precisa guardar informações como o valor base, as diferentes opções de pagamento com seus descontos ou parcelamentos, e se o preço está ativo ou dentro de um período promocional. Nosso foco é sempre o **preço de venda final** para o consumidor.

## 3. Tipos de Preço na Prática 🎭

O `pc-preco` precisa lidar com diversos cenários de precificação que o cliente encontra na loja:

* **Preço Padrão:** O valor normal do produto, geralmente associado a um "preço base" cadastrado.
* **Preço "De/Por":** A clássica apresentação onde um "preço base" mais alto ("De") é mostrado riscado, e um preço final mais baixo ("Por") é destacado, geralmente resultante de um desconto para pagamento à vista ou uma promoção geral.
* **Preço com Desconto Específico (Ex: Pix):** Exibição de um preço ainda menor se o cliente optar por uma forma de pagamento específica que a plataforma deseja incentivar (ex: um "percentual de desconto" só para Pix).
* **Preço Parcelado:** A capacidade de exibir opções de pagamento em várias vezes ("10x de R$...", "12x de R$...") , informando claramente o valor de cada parcela.
* **Parcelamento Com e Sem Juros:** Diferenciar claramente até quantas parcelas o cliente pode pagar sem acréscimo ("sem juros") e quais opções (geralmente com mais parcelas) terão juros aplicados, informando as condições.
* **Preço Promocional:** Preços especiais que são válidos apenas durante um período específico (definido por "datas de início e fim de validade"). Isso é essencial para campanhas como Black Friday, Dia do Consumidor, etc.

## 4. Lógica de Cálculos Que o `pc-preco` Realiza 🧮

Nosso microsserviço não é só um "depósito" de dados, ele também realiza cálculos cruciais para apresentar as informações corretas:

* **Cálculo do Preço à Vista com Desconto:** Quando uma forma de pagamento (como Pix) tem um "percentual de desconto" associado, o `pc-preco` aplica esse percentual sobre o "preço base" para determinar o valor final que o cliente pagará à vista naquela condição.
* **Geração das Opções de Parcelamento (Com/Sem Juros):** Para opções de pagamento parceláveis, o `pc-preco` calcula o valor de cada opção de parcela. Se o número de parcelas ultrapassar um "limite sem juros" pré-definido, ele aplica uma "taxa de juros" configurada. Uma fórmula financeira padrão para calcular o valor de parcelas fixas com juros é a **Tabela Price**:

    $$P = \frac{V \cdot i}{1 - (1 + i)^{-n}}$$

    **Entendendo a Fórmula:**

    * **$P$**: Valor da Parcela (é o que queremos descobrir).
    * **$V$**: Valor Presente (o preço à vista do produto ou o valor que está sendo financiado).
    * **$i$**: Taxa de juros por período (ex: taxa mensal). **Importante:** Deve ser usada na forma decimal (ex: 2,5% ao mês = 0,025).
    * **$n$**: Número de períodos (o número total de parcelas do financiamento).

    #### 📌 Exemplo de Cálculo de Parcela com Juros:

    Vamos supor os seguintes dados:

    * Preço Base (V): R$ 1.000,00
    * Número de Parcelas (n): 12x
    * Taxa de Juros (i): 2,5% ao mês (ou 0,025)
    * Limite Sem Juros: 10x (Como 12x > 10x, aplicamos juros)

    Aplicando na fórmula:
    $$P = \frac{1000 \cdot 0{,}025}{1 - (1 + 0{,}025)^{-12}}$$
    $$P = \frac{25}{1 - (1{,}025)^{-12}}$$
    $$P \approx \frac{25}{1 - 0{,}743555...}$$
    $$P \approx \frac{25}{0{,}256444...}$$

    **Valor aproximado da parcela (P): R$ 97,49** *(Nota: O valor pode variar ligeiramente dependendo do arredondamento nos cálculos intermediários. O exemplo original dava R$96,22, mantivemos o cálculo refeito aqui para consistência com a fórmula apresentada).*

    **Preço total final** (neste parcelamento) = $$12 \times 97,49 = 1169,88$$ **Resultado Final: R$ 1.169,88**

    O `pc-preco` deve realizar este cálculo para cada opção de parcela acima do limite sem juros e armazenar/apresentar o `valor da parcela` e o `valor total final`.

    *(Nota Técnica Importante: Embora o `pc-preco` deva ser capaz de calcular o Custo Efetivo Total (**CET** - o custo total do financiamento, incluindo juros e outras taxas, exigido por lei) para conformidade regulatória, nossa pesquisa indica que muitos varejistas só exibem essa informação detalhada no checkout, e não na página de produto inicial).*

## 5. Regras de Negócio e Validações: Mantendo a Ordem! ✅🚦

Aplicamos regras para garantir a qualidade dos dados e o alinhamento com as expectativas do mercado, fundamentadas em nossa pesquisa (benchmarking).

* **REGRA 1: Validação Interna de Dados Essenciais**
    * **Descrição:** `pc-preco` verifica se dados mínimos para um preço existir estão presentes e válidos (ex: associação a um `productId` e `sellerId`, valor base numérico, moeda válida).
    * **Justificativa / Prática de Mercado:** Garante a integridade básica dos dados, evitando que produtos apareçam sem preço ou com informações quebradas. É um princípio fundamental de **data governance** (governança de dados, ou seja, cuidar bem dos nossos dados!).
* **REGRA 2: Consistência das Regras de Parcelamento**
    * **Descrição:** `pc-preco` valida se as regras de parcelamento são lógicas (ex: o número máximo de parcelas permitido é maior ou igual ao limite de parcelas sem juros).
    * **Justificativa / Prática de Mercado:** Previne erros de cálculo e exibições confusas para o cliente, assegurando que as opções de parcelamento sejam apresentadas corretamente.
* **REGRA 3: Suporte a Descontos Agressivos para Pagamento à Vista (Especialmente Pix)**
    * **Descrição:** Permitir a configuração flexível de um "percentual de desconto" atrelado a formas de pagamento específicas, com destaque para o Pix (ex: 10% de desconto). O Boleto geralmente não tem desconto adicional.
    * **Justificativa / Prática de Mercado:** **Fundamental.** Nossa pesquisa mostrou que descontos no Pix (frequentemente 7-15%) são uma prática dominante e estratégica dos grandes players (Magalu, Via, Kabum!, ML) para reduzir custos de transação e atrair clientes sensíveis a preço. O `pc-preco` precisa suportar isso nativamente.
* **REGRA 4: Suporte a Limite de Parcelamento Sem Juros (Padrão de Mercado)**
    * **Descrição:** Permitir configurar um "limite de parcelas sem juros" (ex: até 10x sem juros) e uma "taxa de juros" para parcelas acima desse limite (ex: de 11x a 12x com juros).
    * **Justificativa / Prática de Mercado:** **Essencial.** O parcelamento sem juros em 10x ou 12x é um padrão esperado pelo consumidor brasileiro para produtos de maior valor, conforme observado em todos os grandes concorrentes. Oferecer isso é crucial para a competitividade. Parcelamentos mais longos geralmente envolvem juros e estão ligados a crédito da loja (Cartão Luiza, Carnê Digital).
* **REGRA 5: Suporte a Preços Promocionais com Validade Temporal**
    * **Descrição:** Permitir que registros de preço tenham "datas de início e fim de validade" para ativar/desativar promoções automaticamente.
    * **Justificativa / Prática de Mercado:** **Indispensável.** Todos os varejistas dependem disso para campanhas de marketing sazonais (Black Friday, etc.), queimas de estoque e ofertas com senso de urgência. A API do `pc-preco` deve permitir criar/atualizar preços com essas datas. Embora a data de fim raramente seja exibida na página de produto, o controle interno de validade é necessário.
* **REGRA 6 (Externa): Precificação Conforme Margens e MSRP**
    * **Descrição:** O preço base cadastrado *deve* respeitar regras de negócio como margem mínima/máxima (baseadas no custo) ou o Preço Sugerido pelo Fabricante (**MSRP** - Manufacturer's Suggested Retail Price). *(Exemplo: Custo R$1000, Margem 20-80% -> Preço Venda entre R$1200 e R$1800)*.
    * **Responsabilidade:** A **validação** desta regra **NÃO** é feita pelo `pc-preco`. Ela ocorre *antes*, no sistema onde o vendedor/administrador cadastra o preço.
    * **Justificativa / Prática de Mercado:** Controle financeiro do vendedor/plataforma e acordos comerciais. O `pc-preco` confia que o preço recebido já foi validado externamente.
* **REGRA 7 (Externa): Preço Influenciado por Estoque ou Reputação**
    * **Descrição:** Regras como "dar 10% de desconto se produto > 30 dias no estoque" ou "permitir preço 10% acima da média se vendedor tem reputação 5 estrelas".
    * **Responsabilidade:** Aplicadas por **sistemas externos**. Eles analisam dados (do `pc-estoque`, `pc-identidade`) e **chamam a API do `pc-preco`** para *criar ou atualizar* um registro de preço específico. O `pc-preco` não age sozinho baseado nesses fatores.
    * **Justificativa / Prática de Mercado:** Permite estratégias de precificação dinâmica ou personalização, mas desacopladas da lógica central de armazenamento e cálculo de preço.

## 6. Responsabilidades: O que `pc-preco` FAZ e NÃO FAZ 👍👎

Manter o foco é a chave para um bom microsserviço!

**O `pc-preco` FAZ:** ✅

* Gerenciar o ciclo de vida completo dos registros de preço (**CRUD** - Create, Read, Update, Delete; as quatro operações básicas de manipulação de dados: Criar, Ler, Atualizar, Deletar).
* Armazenar e calcular condições detalhadas por forma de pagamento (descontos, parcelas).
* Calcular preços finais à vista e os valores exatos das parcelas (com ou sem juros).
* Controlar a ativação/desativação de preços com base em status e datas de validade.
* Fornecer uma **API** clara e bem definida para outros sistemas interagirem com os dados de preço.

**O `pc-preco` NÃO FAZ:** ⛔

* Calcular **frete** (tarefa do `pc-frete`).
* Controlar o **estoque** (tarefa do `pc-estoque`).
* Armazenar **dados descritivos ou técnicos completos** dos produtos (tarefa do `pc-catalogo`).
* Armazenar **dados cadastrais detalhados ou reputação** de vendedores (tarefa do `pc-identidade`).
* Validar preços contra **custo** do produto ou **margem de lucro** interna do vendedor.
* Executar automaticamente regras que dependam de monitoramento ativo de outros microsserviços.

## 7. Interações e APIs: Como o `pc-preco` "Conversa" 🤝💬

Microsserviços se comunicam via **APIs**. Pense numa API como um "contrato de comunicação" ou um "garçom digital" que recebe pedidos (requisições) de outros sistemas e entrega respostas padronizadas. Isso permite que tudo funcione junto sem um sistema precisar conhecer os detalhes internos do outro.

* **Endpoints da API:** Nossa API terá **Endpoints**, que são os "endereços" específicos na rede para cada operação. Exemplos conceituais:
    * `GET /prices?productId=...&sellerId=...`: Para buscar os preços ativos de um produto/vendedor.
    * `POST /prices`: Para criar um novo registro de preço.
    * `PUT /prices/{priceId}`: Para atualizar um preço existente.

*(O design detalhado da API, incluindo os formatos de dados, geralmente **JSON** (JavaScript Object Notation - um formato leve e legível de texto para troca de dados entre sistemas) será um próximo passo nosso!)*

## 8. Benchmarking e Referências de Mercado 📊🎯

Analisamos as práticas dos gigantes do e-commerce brasileiro (Magazine Luiza, Mercado Livre, Amazon BR, Via Varejo, Kabum!) para entender o cenário competitivo e as expectativas dos clientes. Isso fundamenta nossas regras e decisões.

**Principais Conclusões da Pesquisa:**

* **Pix é Estratégico:** Descontos agressivos (7-15%+) são a norma para Pix, refletindo seus baixos custos e liquidez rápida para o varejista. É crucial ter flexibilidade para configurar esses descontos. O Boleto perdeu força promocional.
* **Parcelamento Sem Juros é Padrão:** 10x ou 12x sem juros são condições esperadas para produtos de maior valor. Oferecer isso é vital para competir. Parcelamentos mais longos geralmente têm juros e estão ligados a crédito da loja.
* **Transparência de Juros Limitada na PDP** (Product Detail Page - a Página de Detalhes do Produto, onde o cliente vê todas as informações de um item específico): Embora o cálculo precise ser feito (incluindo CET para conformidade), a exibição detalhada de taxas de juros na página de produto não é prática comum; geralmente aparece só no checkout.
* **Apresentação Visual:** O formato "De/Por" e selos de desconto são universais. A validade explícita de promoções na página de produto é rara. A hierarquia visual do bloco de preço varia (alguns destacam mais o Pix, outros a parcela).
* **Marketplace:** Modelos de "Buy Box" (Amazon, ML) vs. "Lista de Ofertas" (Via) coexistem. A forma como a concorrência é apresentada impacta a estratégia de preço.
* **Frete:** O cálculo é sempre separado e exige localização (CEP). A comunicação de frete grátis é destaque, mas quase sempre condicional (valor mínimo, região, etc.).

## 9. Próximos Passos para o Time `pc-preco` 🚀

Com esta base sólida sobre o *quê* e o *porquê* do `pc-preco`, nossos próximos passos focam no *como*:

1.  **Refinar Regras e Atributos Conceituais:** Validar se as regras cobrem todos os cenários iniciais e se precisamos pensar em mais algum atributo chave (conceitualmente) para suportá-las.
2.  **Desenhar a API:** Detalhar os **endpoints**, métodos (**GET, POST, PUT, DELETE** - são 'verbos' do protocolo HTTP que indicam a ação desejada em uma API: GET para buscar dados, POST para criar, PUT para atualizar/substituir, e DELETE para remover) e os formatos de dados (**JSON**) para a comunicação. Este será nosso "contrato" de comunicação.
3.  **Prototipagem/PoC** (Proof of Concept - Prova de Conceito, um pequeno experimento para testar se uma ideia ou tecnologia funciona): Considerar implementar um endpoint muito simples para testar ideias e validar abordagens técnicas iniciais (sem definir a tecnologia final ainda).
4.  **Definir Estratégia de Testes:** Planejar como vamos garantir a qualidade e a corretude dos cálculos e regras.
5.  **Planejar o Desenvolvimento:** Quebrar o trabalho em tarefas menores (histórias de usuário) e priorizar as funcionalidades essenciais para as primeiras entregas (Sprints).

---
Este documento é nosso ponto de partida! Ele deve evoluir à medida que avançamos. Qualquer dúvida ou sugestão, vamos conversar! 🗣️