import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from soccerplots.radar_chart import Radar
from mplsoccer import PyPizza
import matplotlib as mpl
import math
from scipy import stats

# Read data
st.title("MTA RADAR Comparison Data is per 90 min")
df = pd.read_csv('https://raw.githubusercontent.com/Galfishman/MTA-Radar/main/Players%20Per%2090.csv')

# Define the mapping of Short Position to Position 1
position_mapping = {
    'Center Backs': ['Right Centre Back', 'Left Centre Back', 'Central Defender'],
    'Full Backs': ['Right Wing Back', 'Right Back', 'Left Wing Back', 'Left Back'],
    'Midfielders': ['Right Midfielder', 'Left Midfielder', 'Defensive Midfielder', 'Centre Attacking Midfielder', 'Central Midfielder'],
    'Wingers': ['Right Winger', 'Right Attacking Midfielder', 'Left Winger', 'Left Attacking Midfielder'],
    'Strikers': ['Second Striker', 'Centre Forward'],
    'GK': ['Goalkeeper'],
}

st.sidebar.header("Please Filter Here:")
selected_position_group = st.sidebar.selectbox("Filter by Position Group:", options=list(position_mapping.keys()))
min_minutes_played = st.sidebar.slider("Filter by Minimum Minutes Played:", 0, int(df['Min'].max()), 0, 1)
filtered_players = df[(df['pos'].isin(position_mapping[selected_position_group])) & (df['Min'] >= min_minutes_played)]
players_list = filtered_players["Player"].unique()
Name = st.sidebar.selectbox("Select the Player:", options=players_list)
Name2 = st.sidebar.selectbox("Select other Player:", options=["League Average"] + filtered_players["Player"].unique().tolist())

# Parameters
all_params = list(df.columns[7:])
selected_params = st.sidebar.multiselect("Select Parameters:", options=all_params, default=("xG", "TchsA3", "TouchOpBox", "SucflDuels", "Success1v1"))

# Setup radar plot
ranges = [(min(df[param]) - (min(df[param]) * 0.2), max(df[param])) for param in selected_params]
a_values = df.loc[df['Player'] == Name, selected_params].values.flatten()
b_values = df.loc[df['Player'] == Name2, selected_params].values.flatten() if Name2 != "League Average" else filtered_players[filtered_players['Player'] != Name][selected_params].mean().tolist()
values = [a_values, b_values]

# Create radar plot
radar = Radar(background_color="#121212", patch_color="#28252C", label_color="#FFFFFF", label_fontsize=10, range_color="#FFFFFF")
fig, ax = radar.plot_radar(ranges=ranges, params=selected_params, values=values, radar_color=['yellow', 'blue'], edgecolor="#222222", linewidth=1, title=dict(title_name=Name, title_color='yellow', title_name_2=Name2, title_color_2='blue', title_fontsize=12))

# Setup pizza plot
player_data = filtered_players.loc[filtered_players['Player'] == Name, selected_params].iloc[0]
percentile_ranks = [math.floor(stats.percentileofscore(filtered_players[param], player_data[param])) for param in selected_params]
baker = PyPizza(params=selected_params, straight_line_color="#000000", straight_line_lw=1, last_circle_lw=1, other_circle_lw=1, other_circle_ls="-.")
fig2, ax2 = baker.make_pizza(percentile_ranks, figsize=(8, 8), param_location=105, kwargs_slices=dict(facecolor="cornflowerblue", edgecolor="#000000", zorder=2, linewidth=1))

# Display plots side by side
col1, col2 = st.columns(2)
with col1:
    st.header("Radar Plot")
    st.pyplot(fig)
with col2:
    st.header("Pizza Plot")
    st.pyplot(fig2)
