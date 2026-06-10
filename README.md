# Statsbomb-open-data-project
# Recoveries até 5 segundos após perda de posse (StatsBomb + Streamlit)

Este projeto analisa eventos de futebol usando dados da StatsBomb Open Data para identificar e visualizar recuperações de bola até 5 segundos, após perda de posse.

A aplicação é interativa e construída com Streamlit, permitindo explorar momentos do jogo e visualizar o contexto espacial com freeze frames.

-------------------------------------------------
#Objetivo

O objetivo principal é:

- Identificar perdas de posse (dispossessed, miscontrol, error)
- Encontrar recuperações de bola nos 5 segundos seguintes
- Visualizar o contexto do momento com freeze frames (jogadores visíveis)
- Explorar a evolução temporal dos eventos no jogo

-------------------------------------------------

#Dados utilizados

Os dados são obtidos diretamente da StatsBomb Open Data:

- Eventos do jogo (`events`)
- Dados de freeze frame 360 (`three-sixty`)

Jogo utilizado:
- Match ID: `4020077` (Spain Women's vs Germany Women's do UEFA women Euro 2025 )

-------------------------------------------------

#Pipeline do projeto

1. Carregamento de dados

- Importação dos datasets diretamente do GitHub
- Conversão de IDs para string
- Criação de coluna `time_sec`


2. Identificação de eventos relevantes

2.1 Perdas de posse:
- Dispossessed
- Miscontrol
- Error

2.2 Recuperações:
- Ball Recovery

3. Ligação temporal entre eventos

Para cada perda de posse:
- procura-se uma recuperação nos 5 segundos seguintes
- se existir → evento é selecionado

4. Filtragem de eventos 360

- Mantém apenas eventos com recuperação válida
- Expande o `freeze_frame` para análise espacial

5. Processamento do freeze frame

- Expansão de listas para colunas individuais
- Separação de coordenadas `x, y`
- Identificação de:
  - Atacantes
  - Defesas

-------------------------------------------------
# Interface Streamlit

1. Slider temporal

Permite selecionar o minuto do jogo:

- intervalo: início → fim do jogo
- atualiza dinamicamente o evento visualizado


2. Informação do momento

Mostra informação como:

- número de ações no evento
- jogadores visíveis
- atacantes
- defensores

-------------------------------------------------

#Visualização do campo

O campo é desenhado com `mplsoccer.Pitch`:

- estilo StatsBomb
- meio-campo completo
- cores diferenciadas para equipas

🔵 Atacantes
- representados a azul

🟡 Defensores
- representados a amarelo

-------------------------------------------------

#Tecnologias utilizadas

- Python
- Streamlit
- Pandas
- Matplotlib
- mplsoccer
- StatsBomb Open Data API (GitHub)

-------------------------------------------------

# O que este projeto permite analisar

- Pressão imediata após perda de bola
- Estrutura defensiva em recuperação
- Posicionamento dos jogadores no momento do evento
- Contexto espacial das ações

-------------------------------------------------

# Como correr o projeto

pip install streamlit 
pip install pandas 
pip install matplotlib 
pip install mplsoccer

Executar a aplicação:
streamlit run App 360 data.py

# xT Live Explorer (StatsBomb + Streamlit)

Este projeto calcula e visualiza um modelo dinâmico de Expected Threat (xT) utilizando dados de eventos da StatsBomb Open Data. A aplicação é interativa e construída com Streamlit, permitindo explorar a evolução do valor ofensivo das diferentes zonas do campo ao longo do jogo.

-------------------------------------------------

# Objetivo

O objetivo deste projeto é o de:
- Construir uma grelha espacial do campo
- Calcular probabilidades de remate por zona
- Calcular probabilidades de golo por zona
- Construir uma matriz de transição através de passes e conduções
- Estimar o valor ofensivo (xT) de cada zona do campo
- Visualizar a evolução temporal do xT durante o jogo

-------------------------------------------------
# Dados utilizados

Os dados são obtidos diretamente da StatsBomb Open Data através da biblioteca `statsbombpy`. O que procuramos para este projeto foram os eventos:
- Eventos do jogo (`events`)
- Passes
- Conduções (Carries)
- Remates

Jogo utilizado:
- Match ID: `4020077` (Spain Women's vs Germany Women's do UEFA women Euro 2025 )

-------------------------------------------------

# Pipeline do projeto

1. Carregamento de dados
- Importação dos eventos através da StatsBomb API
- Filtragem da equipa em análise
- Conversão dos minutos e segundos para `time_sec`
- Ordenação cronológica dos eventos

2. Navegação temporal

Através de um slider temporal, a aplicação permite selecionar qualquer instante do jogo que compreende qualque momento desde o inicio do jogo, até à sua conclusão.

Todos os eventos posteriores ao instante selecionado são removidos da análise.

3. Construção da grelha espacial

O campo da StatsBomb (120m x 80m) é dividido em:

- 16 colunas
- 12 linhas
criando assim uma zona espacial de 192 células, todas com a mesma dimensão. Cada evento analisado é atribuído à respetiva célula da grelha.

4. Contagem de ações

Foram contabilizadas para esta análise, todas as ações de Passes, Carries e Remates, sendo posteriormente atribuído a cada célula o total de ações (todas as ações na sua globalidade), Número de remates e quais desses remates resultaram em golo.

5. Cálculo das probabilidades

Foi calculado, para cada zona da grelha as seguintes probabilidades:

- Probabilidade de remate
- Probabilidade de golo
- Probabilidade de "não golo"
- Probabilidade de progressão


6. Construção da matriz de transição

Foi calculada a matriz de transição de bola, com as coordenadas de x/y e end_x/end_y, criando uma ligação entre zona inicial e zona final da ação (passe & carry)

Estas ligações são utilizadas para construir uma matriz de transição que representa a movimentação da bola entre zonas do campo.

7. Cálculo do Expected Threat

O modelo utiliza um processo iterativo baseado em:

- recompensa por remates
- recompensa adicional por golos
- probabilidades de progressão
- matriz de transição

O algoritmo executa múltiplas iterações até convergência dos valores de xT.

8. Normalização dos valores

Os valores finais são:
- normalizados
- convertidos para escala visual
para melhorar a interpretação do mapa de calor.

-------------------------------------------------
# Interface Streamlit

1. Slider temporal

Permite selecionar qualquer instante do jogo no intervalo que atribuirmos, que no caso compreende os momentos entre início → fim do jogo, atualizando a  dinâmica dos cálculos de xT.


2. Informação temporal

Mostra o minuto e segundo correspondentes ao instante selecionado no slider.

-------------------------------------------------

# Visualização do campo

1. O campo é desenhado com `mplsoccer.Pitch`:

- estilo StatsBomb
- campo completo
- mapa de calor dinâmico

2. Escala de cores

As zonas são representadas através de um gradiente:

Zonas mais quentes:
- maior valor de xT
- maior potencial ofensivo

Zonas mais frias
- menor valor de xT
- menor ameaça ofensiva

3. Barra de cor

Inclui uma legenda contínua para interpretação dos valores de Expected Threat.

-------------------------------------------------

# Tecnologias utilizadas

- Streamlit
- Pandas
- NumPy
- Matplotlib
- mplsoccer
- StatsBombPy

-------------------------------------------------

# O que este projeto permite analisar

- Evolução da ameaça ofensiva ao longo do jogo
- Zonas mais perigosas da equipa
- Progressão da posse de bola
- Impacto espacial de passes e conduções
- Dinâmica ofensiva em diferentes momentos da partida
- 
---
# Como correr o projeto

```bash
pip install streamlit
pip install pandas
pip install numpy
pip install matplotlib
pip install mplsoccer
pip install statsbombpy
```

Executar a aplicação:

streamlit run app.py

