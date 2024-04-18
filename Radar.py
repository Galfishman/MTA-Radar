import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from soccerplots.radar_chart import Radar
from mplsoccer import PyPizza
import matplotlib as mpl
from io import BytesIO
from mplsoccer import PyPizza, FontManager
import matplotlib as mpl
import math
from scipy import stats






###login
st.title("MTA RADAR Comparison Data is per 90 min")

# READ DATA
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

# Filter by position group
selected_position_group = st.sidebar.selectbox(
    "Filter by Position Group:",
    options=list(position_mapping.keys()),
)

# Filter by Minutes Played (Min)
min_minutes_played = st.sidebar.slider("Filter by Minimum Minutes Played:", min_value=0, max_value=int(df['Min'].max()), step=1, value=0)

# Filter the DataFrame based on the selected position group and minimum minutes played
filtered_players = df[(df['pos'].isin(position_mapping[selected_position_group])) & (df['Min'] >= min_minutes_played)]

# List of players based on the selected position group
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
all_params = list(df.columns[19:])

# Filtered parameters based on user selection
selected_params = st.sidebar.multiselect(
    "Select Parameters:",
    options=all_params,
    default=("xG", "TchsA3", "TouchOpBox", "SucflDuels", "Success1v1"))  # Default value is all_params (all parameters selected)

params = selected_params

with st.expander("Show Players Table"):
    # Display the DataFrame with only selected parameters
    selected_columns = ['Player','Team','Min'] + selected_params
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
        minutes_player2 = player2_row['Min'].values[0]
        Position_name2 = player2_row['pos'].values[0]
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
minutes_name = "Min"
minutes_player1 = filtered_players.loc[filtered_players['Player'] == Name, minutes_name].values[0]

Position_name = "pos"
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

mpl.rcParams['figure.dpi'] = 1500


##########################################
##########################################
##########################################
##########################################


player_data = filtered_players.loc[filtered_players['Player'] == Name, selected_params].iloc[0]
# Calculate percentiles for Name
values_name = [
    math.floor(stats.percentileofscore(filtered_players[param], player_data[param]))
    for param in selected_params
]

# Fetch player data for Name2 if not 'League Average'
if Name2 != "League Average":
    player_data2 = filtered_players.loc[filtered_players['Player'] == Name2, selected_params].iloc[0]
    values_name2 = [
        math.floor(stats.percentileofscore(filtered_players[param], player_data2[param]))
        for param in selected_params
    ]
else:
    # Calculate league average values if Name2 is 'League Average'
    league_average_data = filtered_players[selected_params].mean()
    values_name2 = [
        math.floor(stats.percentileofscore(filtered_players[param], league_average_data[param]))
        for param in selected_params
    ]

# Create a table to display the statistic names and values
table_data = {'Statistic': selected_params, 'Value': player_data[selected_params]}
table_df = pd.DataFrame(table_data)
### PRECEPLIE PIZZA
# Configuring the pizza plot
baker = PyPizza(
    params=selected_params,                  # list of parameters
    straight_line_color="white",             # color for straight lines
    straight_line_lw=2,                      # linewidth for straight lines
    last_circle_lw=3,                        # linewidth of last circle
    last_circle_color='white',               # color of last circle
    other_circle_lw=1,                       # linewidth for other circles
    other_circle_color='grey',               # color of other circles
    other_circle_ls="-."                     # linestyle for other circles
)

# Create pizza plot with values for both players
fig, ax = baker.make_pizza(
    [values_name, values_name2],            # list of two players' values
    compare=True,                           # enable comparison
    figsize=(10, 10),                       # figure size
    param_location=105,                     # parameter label location
    kwargs_slices=dict(
        facecolor=["cornflowerblue", "salmon"],  # colors for each player's slices
        edgecolor='white',                  # edge color of slices
        zorder=2,                           # drawing order
        linewidth=3                         # slice border linewidth
    ),
    kwargs_params=dict(
        color="white",                      # parameter label color
        fontsize=10,                        # parameter label fontsize
        va="center"                         # alignment of parameter labels
    ),
    kwargs_compare=dict(
        colors=["white", "white"],          # colors for text in compare mode
        zorder=3,                           # drawing order for text
        bbox=dict(
            edgecolor="white",              # box edge color
            facecolor=["cornflowerblue", "salmon"],  # box face color
            boxstyle="round,pad=0.2",       # box style
            lw=1                            # box line width
        )
    )
)
fig.patch.set_facecolor('#121212')  # Set background color for the figure
ax.set_facecolor('#121212')         # Set background color for the axes

# Adding titles and annotations as needed
title = f"Comparison of {Name} and {Name2}\nPercentile Ranks"
fig.text(0.5, 0.97, title, size=18, ha="center", color="white", fontweight="bold")

# Show plot in Streamlit
st.pyplot(fig)




param_value_text = f"{Name}  Values\n"
for param, value in zip(selected_params, player_data):
    param_value_text += f"{param} - {value}\n"

# Adjust the vertical position of the param_value_text box based on the number of parameters
num_params = len(selected_params)
param_value_y = -0.11 - (num_params * 0.015)  # Adjust the value as needed to control the vertical position


# Display plots side by side with a gap
col1, col2 = st.columns([1, 1], gap='large') 
with col1:
    st.header("Values Radar ")
    st.pyplot(fig)
with col2:
    st.header("Percentile Rank")
    st.pyplot(fig2)






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
