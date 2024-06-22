import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from soccerplots.radar_chart import Radar
import matplotlib as mpl

# Set the default font family for Matplotlib
mpl.rcParams['figure.dpi'] = 2400

st.title("MTA RADAR Comparison")
# READ DATA
df = pd.read_csv('https://raw.githubusercontent.com/Galfishman/MTA-Radar/main/pages/Leumit%20Players.csv')
Team = "teamName"

# Ensure 'Minutes played' is numeric and handle non-numeric gracefully
df['Minutes played'] = pd.to_numeric(df['Minutes played'], errors='coerce')

position_mapping = {
    "All": "",
    "Wingers": ["LM", "RM", "LAM", "RAM"],
    "Strikers": ["CF", "LCF", "RCF"],
    "Midfielders": ["CAM", "LCAM", "RCAM", "CDM", "LCDM", "RCDM", "LCM", "RCM"],
    "Defenders": ["CD", "LCD", "RCD", "LD", "RD"],
}

st.sidebar.header("Please Filter Here:")

# Filter by position group
selected_position_group = st.sidebar.selectbox(
    "Filter by Position Group:",
    options=list(position_mapping),
)

max_value_placeholder = 6000  # Use a large placeholder value
min_minutes_played = st.sidebar.slider(
    "Filter by Minimum Minutes Played:",
    min_value=0,
    max_value=max_value_placeholder,
    step=1,
    value=0
)

# Check if the selected position group is empty and handle it
if selected_position_group == "All":
    filtered_players = df[df['Minutes played'] >= min_minutes_played]
else:
    filtered_players = df[
        df["Position"].str.contains("|".join(position_mapping[selected_position_group]), case=False, na=False) & 
        (df['Minutes played'] >= min_minutes_played)
    ]

players_list = filtered_players["Player"].unique()

Name = st.sidebar.selectbox(
    "Select the Player:",
    options=players_list,
)

Name2 = st.sidebar.selectbox(
    "Select other Player:",
    options=["League Average"] + filtered_players["Player"].unique().tolist(),
)

Name3 = st.sidebar.selectbox(
    "Select third Player (optional):",
    options=["None"] + filtered_players["Player"].unique().tolist(),
    index=0  # Default to "None"
)

# List of all available parameters
all_params = list(df.columns[9:])

# Filtered parameters based on user selection
selected_params = st.sidebar.multiselect(
    "Select Parameters:",
    options=all_params,
    default=("xG", "xA", "Actions unsuccessful", "Actions successful", "Final third entries through pass","Lost balls"))  # Default value is all_params (all parameters selected)

params = selected_params

with st.expander("Show Players Table"):
    # Display the DataFrame with only selected parameters
    selected_columns = ['Player','Team','Minutes played','Position'] + selected_params
    st.dataframe(filtered_players[selected_columns])

# add ranges to list of tuple pairs
ranges = []
a_values = []
b_values = []
c_values = []

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
    if Name3 != "None" and row['Player'] == Name3:
        c_values = row[params].tolist()

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
        title_name2 = f"{Name2}\n{'Team:  ' + team_name2}\n{'Position: ' + Position_name2}\n{minutes_player2} Minutes Played"
    else:
        st.error(f"No data available for player: {Name2}")
        st.stop()

if Name3 != "None":
    player3_row = df[df['Player'] == Name3]
    if not player3_row.empty:
        minutes_player3 = player3_row['Minutes played'].values[0]
        Position_name3 = player3_row['Position'].values[0]
        team_name3 = player3_row['Team'].values[0]
        c_values = player3_row[params].values[0].tolist()
        title_name3 = f"{Name3}\n{'Team:  ' + team_name3}\n{'Position: ' + Position_name3}\n{minutes_player3} Minutes Played"
    else:
        st.error(f"No data available for player: {Name3}")
        st.stop()
else:
    title_name3 = None
    c_values = []

a_values = a_values[:]
b_values = b_values[:]
values = [a_values, b_values]
if c_values:
    values.append(c_values)

# Print values for troubleshooting
minutes_name = "Minutes played"
minutes_player1 = filtered_players.loc[filtered_players['Player'] == Name, minutes_name].values[0]

Position_name = "Position"
Position_name1 = filtered_players.loc[filtered_players['Player'] == Name, Position_name].values[0]

Team_name = "Team"
team_name1 = filtered_players.loc[filtered_players['Player'] == Name, Team_name].values[0]

# Update the title dictionary with minutes played
title = dict(
    title_name=f"{Name}\n{'Team: ' + team_name1}\n{'Position: '+Position_name1}\n{minutes_player1} Minutes Played",
    title_color='yellow',
    title_name_2=title_name2,
    title_name3=title_name3,
    title_color_2='blue',
    title_color_3='green',

    title_fontsize=12,
)

if title_name3:
    title["title_name_3"] = title_name3
    title["title_color_3"] = 'green'

# RADAR PLOT
radar = Radar(
    background_color="#121212",
    patch_color="#28252C",
    label_color="#FFFFFF",
    label_fontsize=8,
    range_color="#FFFFFF"
)

# plot radar
fig, ax = radar.plot_radar(
    ranges=ranges,
    params=params,
    values=values,
    radar_color=['yellow', 'blue', 'red'] if c_values else ['yellow', 'blue'],
    edgecolor="#222222",
    zorder=2,
    linewidth=1,
    title=title,
    alphas=[0.4, 0.4, 0.4] if c_values else [0.4, 0.4],
    compare=True
)

# Manually add the third title if it exists
if title_name3:
    fig.text(0.5, 0.92, title_name3, ha='center', fontsize=12, color='red',weight='bold')
st.pyplot(fig)

head_to_head_df = pd.DataFrame({
    'Player': [Name, Name2] + ([Name3] if Name3 != "None" else []),
    **{param: [a_values[i], b_values[i]] + ([c_values[i]] if c_values else []) for i, param in enumerate(params)}
})

# Transpose the DataFrame to have parameters as rows
head_to_head_df_transposed = head_to_head_df.set_index('Player').T

# Identify the highest value for each parameter across both players
max_values = head_to_head_df_transposed.max()

# Highlight the highest value in each row across both players
highlighted_df = head_to_head_df_transposed.style.format("{:.2f}").apply(lambda row: ['background-color: grey' if val == row.max() else '' for val in row], axis=1)

st.header("Head-to-Head Comparison")
st.table(highlighted_df)
