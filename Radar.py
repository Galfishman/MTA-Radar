import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from soccerplots.radar_chart import Radar
from mplsoccer import PyPizza
import matplotlib as mpl
import pickle
from pathlib import Path

###login

# READ DATA
@st.cache_data  # Cache the result of this function
def load_data():
    return pd.read_csv('https://raw.githubusercontent.com/Galfishman/MTA-Radar/main/DataBase.csv')

rawdf = load_data()


st.title("MTA Radar Compression")
# READ DATA
#rawdf = pd.read_csv('https://raw.githubusercontent.com/Galfishman/MTA-Radar/main/DataBase.csv')


st.sidebar.header("Please Filter Here:")

min_selection = st.sidebar.slider('Minutes played:',
                                  min_value=int(rawdf['Minutes played'].min()),
                                  max_value=int(rawdf['Minutes played'].max()),
                                  value=(int(rawdf['Minutes played'].min()), int(rawdf['Minutes played'].max())))
filtered_df = rawdf[(rawdf['Minutes played'] >= min_selection[0]) & (rawdf['Minutes played'] <= min_selection[1])]


position_options = {
    "All": "",
    "Wingers": ["rw", "lw", "lam", "ram"],
    "Strikers": ["cf", "st"],
    "Midfielders": ["cmf", "dmf", "rcmf", "lcmf", "amf","LCMF"],
    "Defenders": ["rb", "cb", "lb", "rcb", "lcb","rwb","lwb"],
}

selected_position = st.sidebar.selectbox("Select Position:", options=list(position_options.keys()))

# Apply position filtering
if selected_position != "All":
    position_filter = rawdf["Position"].str.contains("|".join(position_options[selected_position]), case=False)
    filtered_df = rawdf[position_filter.fillna(False)]
else:
    filtered_df = rawdf

df = filtered_df

# Display the filtered DataFrame

# Create or retrieve session state
if 'state' not in st.session_state:
    st.session_state.state = {'selected_leagues': [], 'selected_player': None, 'Name': None, 'Name2': None}

# Filter by league
all_leagues = df["League"].unique()
all_leagues = ['All'] + all_leagues.tolist()
selected_leagues = st.multiselect("Select League:", options=all_leagues, default=["All"])

# Store selected leagues in session state
st.session_state.state['selected_leagues'] = selected_leagues

if "All" in selected_leagues:
    df = df  # No filtering needed if "All" is selected
else:
    df = df[df["League"].isin(selected_leagues)]

# Retrieve or initialize Name and Name2 from session state
Name = st.session_state.state.get('Name')
Name2 = st.session_state.state.get('Name2')

# Select the Player
player_options = df["Player"].unique().tolist()
player_options2 = ["League Average"] + df["Player"].unique().tolist()
Name = st.sidebar.selectbox(
    "Select the Player:",
    options=player_options,
    index=player_options.index(Name) if Name in player_options else 0,
    key='NameSelector',
)
Name2 = st.sidebar.selectbox(
    "Select other Player:",
    options=player_options2,
    index=player_options2.index(Name2) if Name2 in player_options2 else 0,
    key='Name2Selector',
)

# Store selected player in session state
st.session_state.state['Name'] = Name
st.session_state.state['Name2'] = Name2

# Rest of the code remains the same...


# Create a collapsible section for the DataFrame
with st.expander("Show Players Table"):
    # Display the DataFrame
    st.dataframe(df)

# List of all available parameters
all_params = list(df.columns[7:])

# Filtered parameters based on user selection
selected_params = st.sidebar.multiselect(
    "Select Parameters:",
    options=all_params,
    default=("Key passes per 90", "Dribbles per 90", "Passes to penalty area per 90", "Shot assists per 90", "Crosses per 90", "Shots per 90", "xG per 90")  # Default value is all_params (all parameters selected)
)

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

for _, row in df.iterrows():
    if row['Player'] == Name:
        a_values = row[params].tolist()
    if row['Player'] == Name2:
        b_values = row[params].tolist()

# Find the minutes played for the selected players
minutes_player1 = df.loc[df['Player'] == Name, 'Minutes played'].values[0]

league_player2 = ""
if Name2 == "League Average":
    league_average_values = df[df['League'] == df.loc[df['Player'] == Name, 'League'].values[0]][params].mean().tolist()
    b_values = league_average_values
    title_name2 = "League Average"
else:
    player2_row = df[df['Player'] == Name2]
    if not player2_row.empty:
        minutes_player2 = player2_row['Minutes played'].values[0]
        Position_name2 = player2_row['Position'].values[0]
        team_name2 = player2_row['Team'].values[0]
        league_player2 = player2_row['League'].values[0]
        b_values = player2_row[params].values[0].tolist()
        title_name2 = f"{Name2}\n{'Position: ' + Position_name2}\n{'Team:  ' + team_name2}\n{'League: ' + league_player2}\n{minutes_player2} Minutes Played"
    else:
        st.error(f"No data available for player: {Name2}")
        st.stop()

a_values = a_values[:]
b_values = b_values[:]
values = [a_values, b_values]

# Update the title dictionary with minutes played
title = dict(
    title_name=f"{Name}\n{'Position: ' + df.loc[df['Player'] == Name, 'Position'].values[0]}\n{'Team:  ' + df.loc[df['Player'] == Name, 'Team'].values[0]}\n{'League: ' + df.loc[df['Player'] == Name, 'League'].values[0]}\n{minutes_player1} Minutes Played",
    title_color='yellow',
    title_name_2=title_name2,
    title_color_2='blue',
    title_fontsize=13,
)

# RADAR PLOT
radar = Radar(
    background_color="#121212",
    patch_color="#28252C",
    label_color="#FFFFFF",
    label_fontsize=9,
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

mpl.rcParams['figure.dpi'] = 2500

st.pyplot(fig)
