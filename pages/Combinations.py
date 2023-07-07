import streamlit as st
import pandas as pd
from itertools import combinations
import matplotlib as plt

# Read player data from the CSV file
df = pd.read_csv('https://raw.githubusercontent.com/Galfishman/MTA-Radar/main/Combinations.csv')

# Get unique teams from the 'Team' column
team_options = df['Team'].unique().tolist()

# Define position options
position_options = {
    "All": "",
    "Wingers": ["rw", "lw", "lam", "ram"],
    "Strikers": ["cf", "st", "rcf", "lcf"],
    "Midfielders": ["cmf", "dmf", "rcmf", "lcmf", "amf", "lcmf"],
    "Defenders": ["rb", "cb", "lb", "rcb", "lcb", "rwb", "lwb"],
}

# Get unique parameters from the DataFrame (excluding the first 7 columns)
parameter_options = df.columns[7:].tolist()

# Streamlit application
st.title("Player Combination Analyzer")
st.write("Select options to analyze player combinations:")

st.sidebar.title("Filter Data")

# Select team
selected_team = st.sidebar.selectbox("Select Team", team_options)

# Select position
selected_position = st.sidebar.selectbox("Select Position", list(position_options.keys()))

min_selection = st.sidebar.slider('Minutes played:',
                                  min_value=df['Minutes played'].min(),
                                  max_value=df['Minutes played'].max(),
                                  value=(df['Minutes played'].min(), df['Minutes played'].max()))
df = df[(df['Minutes played'] >= min_selection[0]) & (df['Minutes played'] <= min_selection[1])]

# Select parameter
selected_parameter = st.selectbox("Select Parameter", parameter_options)

# Select threshold score
threshold_score = st.number_input("Enter Parameter Score", min_value=0.0, step=0.1)

# Select number of players in combinations
num_players = st.number_input("Select Number of Players in Combinations", min_value=1, max_value=6, value=3)
# Select number of combinations to display

num_combinations = st.number_input("Enter Number of Combinations", min_value=1)

# Select players to exclude

# Filter data based on selected team and position
filtered_data = df[df['Team'] == selected_team]

players_to_exclude = st.sidebar.multiselect("Select Players to Exclude", filtered_data['Player'].tolist())


if selected_position != "All":
    position_filter = filtered_data["Position"].str.contains("|".join(position_options[selected_position]), case=False)
    filtered_data = filtered_data[position_filter.fillna(False)]

# Exclude selected players
filtered_data = filtered_data[~filtered_data['Player'].isin(players_to_exclude)]

# Reset index of filtered data
filtered_data.reset_index(drop=True, inplace=True)

# Create a dictionary of player scores based on the selected parameter
player_data = filtered_data.set_index('Player')[selected_parameter].to_dict()

# Find and display the selected number of combinations of players
combinations_with_scores = []
for combination in combinations(player_data.keys(), num_players):
    total_score = sum(player_data[player] for player in combination)

    if total_score > threshold_score:
        combinations_with_scores.append((combination, total_score))

# Sort combinations by score in descending order
combinations_with_scores.sort(key=lambda x: x[1], reverse=True)

# Display the selected number of combinations
st.header("Top Combinations")
for i, (combination, total_score) in enumerate(combinations_with_scores[:num_combinations]):
    st.subheader(f"Combination {i+1}")
    st.write("Players:", combination)
    st.write("Score:", total_score)
    st.write("---")
