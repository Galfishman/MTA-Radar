import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from soccerplots.radar_chart import Radar
from mplsoccer import PyPizza
import matplotlib as mpl
import seaborn as sns
from seaborn import swarmplot
import numpy as np
from scipy import stats
import math
import matplotlib as mpl

# Set the default font family for Matplotlib
plt.rcParams['font.family'] = 'Arial'  # You can replace 'Arial' with any font available on your system


st.title("MTA RADAR Comparison")
# READ DATA
df = pd.read_csv('/Users/galfishman/Desktop/Leumit Players.csv')
Team = "teamName"


position_mapping = {
    "All": "",
    "Wingers": ["rw", "lw", "lam", "ram"],
    "Strikers": ["cf", "st","rcf","lcf"],
    "Midfielders": ["cmf", "dmf", "rcmf", "lcmf", "amf","LCMF"],
    "Defenders": ["rb", "cb", "lb", "rcb", "lcb","rwb","lwb"],
}


st.sidebar.header("Please Filter Here:")

# Filter by position group
selected_position_group = st.sidebar.selectbox(
    "Filter by Position Group:",
    options=list(position_mapping),
)

# Filter by Minutes Played (Min)
min_minutes_played = st.sidebar.slider("Filter by Minimum Minutes Played:", min_value=0, max_value=df['Minutes played'].max(), step=1, value=0)

# Filter the DataFrame based on the selected position group and minimum minutes played
filtered_players = df[df["Position"].str.contains("|".join(position_mapping[selected_position_group]), case=False) & (df['Minutes played'] >= min_minutes_played)]
players_list = filtered_players["Player"].unique()



Name = st.sidebar.selectbox(
    "Select the Player:",
    options=players_list,
)

Name2 = st.sidebar.selectbox(
    "Select other Player:",
    options=["League Average"] +filtered_players["Player"].unique().tolist(),
)


    
# List of all available parameters
all_params = list(df.columns[7:])

# Filtered parameters based on user selection
selected_params = st.sidebar.multiselect(
    "Select Parameters:",
    options=all_params,
    default=("xG", "xA", "Duels per 90", "Passes per 90", "Touches in box per 90","Dribbles per 90","Crosses per 90"))  # Default value is all_params (all parameters selected)

params = selected_params

with st.expander("Show Players Table"):
    # Display the DataFrame with only selected parameters
    selected_columns = ['Player','Team','Minutes played','Position'] + selected_params
    st.dataframe(filtered_players[selected_columns])


# add ranges to list of tuple pairs
ranges = []
a_values = []
b_values = []

for x in params:
    a = min(df[x])
    a = a - (a * 0.2)

    b = max(df[x])
    b = b

    ranges.append((a, b))

for _, row in df.iterrows():
    if row['Player'] == Name:
        a_values = row[params].tolist()
    if row['Player'] == Name2:
        b_values = row[params].tolist()


if Name2 == "League Average":
    league_average_values = filtered_players[filtered_players['Player'] != Name][params].mean().tolist()
    b_values = league_average_values
    title_name2 = "League Average"
else:
    player2_row = df[df['Player'] == Name2]
    if not player2_row.empty:
        minutes_player2 = player2_row['Minutes played'].values[0]
        Position_name2 = player2_row['Position'].values[0]
        team_name2 = player2_row['Team'].values[0]
        b_values = player2_row[params].values[0].tolist()
        title_name2 = f"{Name2}\n{'Position: ' + Position_name2}\n{'Team:  ' + team_name2}\n{minutes_player2} Minutes Played"
    else:
        st.error(f"No data available for player: {Name2}")
        st.stop()

a_values = a_values[:]
b_values = b_values[:]
values = [a_values, b_values]

# Print values for troubleshooting
minutes_name = "Minutes played"
minutes_player1 = filtered_players.loc[filtered_players['Player'] == Name, minutes_name].values[0]

Position_name = "Position"
Position_name1 = filtered_players.loc[filtered_players['Player'] == Name, Position_name].values[0]

Team_name = "Team"
team_name1 = filtered_players.loc[filtered_players['Player'] == Name, Team_name].values[0]

# Update the title dictionary with minutes played
title = dict(
    title_name=f"{Name}\n{'Team: ' + team_name1}\n{Position_name1}\n{minutes_player1} Minutes Played",
    title_color='yellow',
    title_name_2= title_name2,
    title_color_2='blue',
    title_fontsize=12,
)

# RADAR PLOT
radar = Radar(
    background_color="#121212",
    patch_color="#28252C",
    label_color="#FFFFFF",
    label_fontsize=10,
    range_color="#FFFFFF"
)

# plot radar
fig, ax = radar.plot_radar(
    ranges=ranges,
    params=params,
    values=values,
    radar_color=['yellow', 'blue'],
    edgecolor="#222222",
    zorder=2,
    linewidth=1,
    title=title,
    alphas=[0.4, 0.4],
    compare=True
)

mpl.rcParams['figure.dpi'] = 2400

st.pyplot(fig)

head_to_head_df = pd.DataFrame({
    'Player': [Name, Name2],
    **{param: [a_values[i], b_values[i]] for i, param in enumerate(params)}
})

# Transpose the DataFrame to have parameters as rows
head_to_head_df_transposed = head_to_head_df.set_index('Player').T

# Identify the highest value for each parameter across both players
max_values = head_to_head_df_transposed.max()

# Highlight the highest value in each row across both players
highlighted_df = head_to_head_df_transposed.style.format("{:.2f}").apply(lambda row: ['background-color: grey' if val == row.max() else '' for val in row], axis=1)

st.header("Head-to-Head Comparison")
st.table(highlighted_df)

