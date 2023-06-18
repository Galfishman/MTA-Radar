import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from soccerplots.radar_chart import Radar
from mplsoccer import PyPizza

import matplotlib as mpl

st.title("Try streamlit")
# READ DATA
df = pd.read_csv('https://raw.githubusercontent.com/Galfishman/MTA-Radar/main/Wing2.csv')

st.dataframe(df)

st.sidebar.header("Please Filter Here:")

Name = st.sidebar.selectbox(
    "Select the Player:",
    options=df["Player"].unique(),
)
Name2 = st.sidebar.selectbox(
    "Select other Player:",
    options=df["Player"].unique(),
)

# List of all available parameters
all_params = list(df.columns[3:])

# Filtered parameters based on user selection
selected_params = st.sidebar.multiselect(
    "Select Parameters:",
    options=all_params,
    default= ("Crosses per 90", "Shots per 90", "xG per 90"))  # Default value is all_params (all parameters selected)

params = selected_params

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

for x in range(len(df['Player'])):
    if df['Player'][x] == Name:
        a_values = df.loc[df['Player'] == Name, params].values.tolist()[0][:]
    if df['Player'][x] == Name2:
        b_values = df.loc[df['Player'] == Name2, params].values.tolist()[0][:]

a_values = a_values[:]
b_values = b_values[:]
values = [a_values, b_values]

# Check and adjust ranges
for i in range(len(ranges)):
    if values[0][i] < ranges[i][0]:
        ranges[i] = (values[0][i], ranges[i][1])
    if values[0][i] > ranges[i][1]:
        ranges[i] = (ranges[i][0], values[0][i])

    if values[1][i] < ranges[i][0]:
        ranges[i] = (values[1][i], ranges[i][1])
    if values[1][i] > ranges[i][1]:
        ranges[i] = (ranges[i][0], values[1][i])

# Print values for troubleshooting

# Find the minutes played for the selected players
League_player = "League"
league_player1 = df.loc[df['Player'] == Name, League_player].values[0]
league_player2 = df.loc[df['Player'] == Name2, League_player].values[0]

minutes_name = "Minutes played"
minutes_player1 = df.loc[df['Player'] == Name, minutes_name].values[0]
minutes_player2 = df.loc[df['Player'] == Name2, minutes_name].values[0]


# Update the title dictionary with minutes played
title = dict(
    title_name=f"{Name}\n({league_player1})\n({minutes_player1} Minutes)",
    title_color='yellow',
    title_name_2=f"{Name2}\n({league_player2})\n({minutes_player2} Minutes)",
    title_color_2='blue',
    title_fontsize=18,
)
# RADAR PLOT
radar = Radar(
    background_color="#121212",
    patch_color="#28252C",
    label_color="#FFFFFF",
    label_fontsize=6.3,
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

mpl.rcParams['figure.dpi'] = 800

st.pyplot(fig)
