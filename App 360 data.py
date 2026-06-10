# Importar alguns modolos que poderão ser necessários
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch


# Configuração da pégina de streamlit que vamos criar
# definição do título a apresentar e definição da totalidade do ecrã
st.set_page_config(page_title="360 - Recoveries after Loss",layout="wide")
st.title("⚽ Recoveries até 5s após perda de posse")

# importação dos dados que vamos utilizar diretamente do github, e do match id= 4020077 (Spain Women's vs Germany Woman's)
match_id = 4020077
df360 = pd.read_json(f"https://raw.githubusercontent.com/statsbomb/open-data/master/data/three-sixty/{match_id}.json")
eventsdf = pd.read_json(f"https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{match_id}.json")

# conversão das colunas da data 360 e event data em string, para que não existam erros na associação
# conversão das colunas minutos e segundos em segundos, criando uma nova coluna
# eliminar possível duplicação de linhas, de forma a não adulterar o dataframe final
df360["event_uuid"] = df360["event_uuid"].astype(str)
eventsdf["id"] = eventsdf["id"].astype(str)
eventsdf["time_sec"] = eventsdf["minute"] * 60 + eventsdf["second"]
events_time = eventsdf[["id", "minute", "second", "time_sec"]].drop_duplicates()


# Faz um merge entre events_time e eventsdf.
# Apenas traz as colunas id e type de eventsdf.
# A ligação é feita pela coluna id.
# how="left" mantém todos os eventos de events_time, mesmo que não exista correspondência em eventsdf.
# o mesmo foi feito para as recoveries
loss_events = events_time.merge(eventsdf[["id", "type"]],on="id",how="left")
loss_events = loss_events[loss_events["type"].apply(
        lambda x: isinstance(x, dict) and x.get("name") in ["Dispossessed", "Miscontrol", "Error"])].copy()

recoveries = events_time.merge(eventsdf[["id", "type"]],on="id",how="left")
recoveries = recoveries[recoveries["type"].apply(
        lambda x: isinstance(x, dict) and x.get("name") == "Ball Recovery")].copy()

# Criação de uma lista vazia onde serão guardados os IDs das recuperações de bola encontradas
# Percorrer todas as perdas de posse presentes em loss_events
# guardar o instante em que as bolas são perdidas, com indicação máxima de 5 segundos
# se as condições forem encontradas, guarda o id das ações
recovery_ids = []

for _, loss in loss_events.iterrows():
    start = loss["time_sec"]
    end = start + 5
    candidate = recoveries[
        (recoveries["time_sec"] >= start) &
        (recoveries["time_sec"] <= end)]
    if len(candidate) > 0:
        recovery_ids.append(candidate.iloc[0]["id"])
recovery_ids = list(set(recovery_ids))

# vamos agora trabalhar a data 360
# Filtra o dataframe df360.
# Mantém apenas as linhas cujo event_uuid está na lista recovery_ids.
# vamos explodir o freeze_frame, fazendo depois a extensão das listas presentes nas colunas
df360 = df360[df360["event_uuid"].isin(recovery_ids)].copy()
freeze = df360[["event_uuid", "freeze_frame"]].explode("freeze_frame")
freeze = pd.concat([freeze.drop(columns=["freeze_frame"]),freeze["freeze_frame"].apply(pd.Series)],axis=1)

# remoção de linhas com location vazia
# expansão das colunas para x e y e eliminamos a coluna location
# preenchimento de valores vazios na coluna teammate
freeze = freeze.dropna(subset=["location"])
freeze[["x", "y"]] = pd.DataFrame(freeze["location"].tolist(),index=freeze.index)
freeze = freeze.drop(columns=["location"])
freeze["teammate"] = freeze["teammate"].fillna(False)

# merge das datasets df360 e events_time
event_times = df360.merge(
    events_time[["id", "time_sec", "minute"]],
    left_on="event_uuid",
    right_on="id",
    how="left")

# pegar no minuto mais baixo da coluna minuto e no minuto mais alto
# criação do slider interativo, com a linha temporal dos eventos
min_minute = int(event_times["minute"].min())
max_minute = int(event_times["minute"].max())
selected_minute = st.slider(
    "Minuto de jogo",
    min_value=min_minute,
    max_value=max_minute,
    value=min_minute)

# Procurar o evento até ao minuto do evento escolhido no slider
# Extrai o freeze frame desse momento e separa o evento entre atacantes e defesas
# filtrar o dataframe para manter apenas as linhas do evento atual
active_events = event_times[event_times["minute"] <= selected_minute]["event_uuid"].unique()
if len(active_events) == 0:
    st.stop()
event_id = active_events[-1]
df_plot = freeze[freeze["event_uuid"] == event_id]
attackers = df_plot[df_plot["teammate"]]
defenders = df_plot[~df_plot["teammate"]]

n_actions = df360[df360["event_uuid"] == event_id].shape[0]


# criação de um título para identificação do bloco
# cria um bloco com informação do momento escolhido no slider
st.markdown("### 📊 Informação do Momento")
st.write(f"""
- 🔁 Ações neste momento: **{n_actions}**
- 👥 Jogadores visíveis (freeze frame): **{len(df_plot)}**
- 🔵 Atacantes: **{len(attackers)}**
- 🟡 Defensores: **{len(defenders)}**""")

# visualização da figura
fig, ax = plt.subplots(figsize=(6, 6), dpi=150)
fig.set_facecolor("#FFFFE5")

pitch = Pitch(
    pitch_type="statsbomb",
    half=False,
    pitch_color="#FFFFE5",
    goal_type="box",
    linewidth=1.25,
    line_color="#002D62",)

pitch.draw(ax=ax)

pitch.scatter(
    attackers["x"],
    attackers["y"],
    ax=ax,
    color="#1E90FF",
    s=40,
    edgecolors="#002D62")

pitch.scatter(
    defenders["x"],
    defenders["y"],
    ax=ax,
    color="#FFD700",
    s=40,
    edgecolors="#002D62")

ax.set_axis_off()
st.pyplot(fig)