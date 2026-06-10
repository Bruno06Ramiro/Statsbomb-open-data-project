# importação dos módulos necessários
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsbombpy import sb
from mplsoccer import Pitch


# Configuração da pégina de streamlit que vamos criar
# definição do título a apresentar e definição da totalidade do ecrã
st.set_page_config(page_title="xT Live Explorer", layout="wide")
st.title("🔥 Expected Threat (xT) Dinâmico no Tempo")

# importação dos dados que pretendemos, utilizando o statsbombpy
# filtragem da equipa a analisar
# criação da coluna ['time_sec'] convertendo os minutos/segundos em segundos, dando depois ordem cronológica aos eventos
match_id = 4020077
events = sb.events(match_id=match_id)
team = "Spain Women's"
events = events[events["team"] == team].copy()
events["time_sec"] = events["minute"] * 60 + events["second"]
events = events.sort_values("time_sec")

# procura do tempo máximo a analisar
# criação de um slider intereativo, com a indicação do tempo máximo de jogo
# Filtragem dos eventos que aconteceram até ao tempo selecionado
max_time = int(events["time_sec"].max())
selected_time = st.slider("Tempo de jogo (segundos)",0,max_time,0)
st.write(f"⏱️ {selected_time//60}:{selected_time%60:02d}")
events = events.loc[events["time_sec"] <= selected_time].copy()

# contrução da nossa grid, para o xT, com 16 linhas e 12 colunas
# bem como a definição do tamanho de cada célula
x = 16
y = 12
length = 120
width = 80
cell_length = length / x
cell_width = width / y

# criação das matrizes em branco, onde depois vão cair a totalidade dos eventos definidos ( shots, passes, carries)
# filtragem dos eventos que vamos procurar
actions_count = np.zeros((y, x))
shots_count = np.zeros((y, x))
goals_count = np.zeros((y, x))
transition_counts = np.zeros((x * y, x * y))

passes = events[events["type"] == "Pass"].copy()
carries = events[events["type"] == "Carry"].copy()
shots = events[events["type"] == "Shot"].copy()

# criação de funções que vão receber as coordenadas e "encaixa-las na respetiva célula, crianda assim uma matriz de ações
def safe_bin(lx, ly):
    xb = min(max(int(lx / cell_length), 0), x - 1)
    yb = min(max(int(ly / cell_width), 0), y - 1)
    return xb, yb

def safe_transition(lx, ly, ex, ey):
    sxb, syb = safe_bin(lx, ly)
    exb, eyb = safe_bin(ex, ey)
    start = syb * x + sxb
    end = eyb * x + exb
    return start, end

# limpar a matriz e garantir de que todas as ações começam do zero

actions_count.fill(0)
shots_count.fill(0)
goals_count.fill(0)
transition_counts.fill(0)

# é aqui que começamos a preencher a grelha
# iteração por todas as linhas do dataset, procurando o evento respetivo
# sempre que encontra o evento, vai encontrar as coordenadas e atribuir à respetiva localização na grelha
# caso encontre uma ação, conta +1
# iteração sobre passes, carries e shots
for _, row in passes.iterrows():
    loc = row.get("location")
    if isinstance(loc, list):
        xb, yb = safe_bin(loc[0], loc[1])
        actions_count[yb, xb] += 1

for _, row in carries.iterrows():
    loc = row.get("location")
    if isinstance(loc, list):
        xb, yb = safe_bin(loc[0], loc[1])
        actions_count[yb, xb] += 1

for _, row in shots.iterrows():
    loc = row.get("location")
    if isinstance(loc, list):
        xb, yb = safe_bin(loc[0], loc[1])
        actions_count[yb, xb] += 1
        shots_count[yb, xb] += 1
        if row.get("shot_outcome") == "Goal":
            goals_count[yb, xb] += 1

# cálculo da probabilidade de haver remate em cada zona, onde as ações são diferentes de 0
# calculada a probabilidade de remate, calculamos a probabilidade de "não remate"
shot_prob = np.divide(
    shots_count,
    actions_count,
    out=np.zeros((y, x)),
    where=actions_count != 0)

goal_prob = np.divide(
    goals_count,
    shots_count,
    out=np.zeros((y, x)),
    where=shots_count != 0)

move_prob = 1 - shot_prob


# iterar sobre todos os passes, procurando as coordenadas iniciais e finais, evitando erros de coordenadas nulas
# convertendo essas coordenadas para a grelha, mostrando a progressão da bola
# o mesmo foi feito para as carries
# contrução da matriz de trasnsição da bola, crinado depois essa probabilidade
successful_passes = passes.copy()

for _, row in successful_passes.iterrows():
    loc = row.get("location")
    end = row.get("pass_end_location")
    if isinstance(loc, list) and isinstance(end, list):
        start, end_idx = safe_transition(
            loc[0], loc[1],
            end[0], end[1])
        transition_counts[start, end_idx] += 1

for _, row in carries.iterrows():
    loc = row.get("location")
    end = row.get("carry_end_location")
    if isinstance(loc, list) and isinstance(end, list):
        start, end_idx = safe_transition(
            loc[0], loc[1],
            end[0], end[1])
        transition_counts[start, end_idx] += 1

row_sums = transition_counts.sum(axis=1, keepdims=True)

transition_matrix = np.divide(
    transition_counts,
    row_sums,
    out=np.zeros_like(transition_counts),
    where=row_sums != 0)


# todas as zonas começam a 0
# atribuição de maior valor aos remates que resultaram em golo

xt = np.zeros(x * y)
reward = shots_count.flatten() + 2 * goals_count.flatten()
for _ in range(100):
    xt_new = reward + (move_prob.flatten() * (transition_matrix @ xt))
    if np.max(np.abs(xt_new - xt)) < 1e-6:
        xt = xt_new
        break
    xt = xt_new
xt_grid = xt.reshape(y, x)
vmin = np.percentile(xt_grid, 5)
vmax = np.percentile(xt_grid, 95)
xt_norm = np.clip((xt_grid - vmin) / (vmax - vmin + 1e-9), 0, 1)

# visualização do grafismo, com a escala de cores e a barra de probabilidades
pitch = Pitch(pitch_type="statsbomb", pitch_color="white", line_color="black")
fig, ax = pitch.draw(figsize=(12, 8))

x_bins = np.linspace(0, 120, x + 1)
y_bins = np.linspace(0, 80, y + 1)

mesh = ax.pcolormesh(
    x_bins,
    y_bins,
    xt_norm,
    cmap="hot",
    shading="auto",
    alpha=0.75)

cbar = plt.colorbar(mesh, ax=ax)
cbar.set_label("Expected Threat (xT)")
ax.set_title(f"xT dinâmico - {selected_time//60}:{selected_time%60:02d}", fontsize=14)

st.pyplot(fig)