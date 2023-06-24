import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from soccerplots.radar_chart import Radar
from highlight_text import fig_text
import numpy as np
from scipy import stats
import math
import matplotlib.image as mpimg
from io import BytesIO
from mplsoccer import PyPizza, FontManager
import matplotlib as mpl

mpl.rcParams['figure.dpi'] = 800

# FONT LOAD
font_normal = FontManager(("https://github.com/google/fonts/blob/main/apache/roboto/static/"
                           "Roboto-Regular.ttf?raw=true"))
font_italic = FontManager(("https://github.com/google/fonts/blob/main/apache/roboto/static/"
                           "Roboto-Italic.ttf?raw=true"))
font_bold = FontManager(("https://github.com/google/fonts/blob/main/apache/roboto/static/"
                         "Roboto-Medium.ttf?raw=true"))


st.title("MTA Percentiles Compression")

# READ DATA
rawdf = pd.read_csv('https://raw.githubusercontent.com/Galfishman/MTA-Radar/main/DataBase.csv')

# Create or retrieve session state
if 'state' not in st.session_state:
    st.session_state.state = {'selected_leagues': None, 'selected_player': None, 'Name': None, 'selected_position':None }




st.sidebar.header("Please Filter Here:")


min_selection = st.sidebar.slider('Minutes played:',
                                  min_value=int(rawdf['Minutes played'].min()),
                                  max_value=int(rawdf['Minutes played'].max()),
                                  value=(int(rawdf['Minutes played'].min()), int(rawdf['Minutes played'].max())))
filtered_df = rawdf[(rawdf['Minutes played'] >= min_selection[0]) & (rawdf['Minutes played'] <= min_selection[1])]


position_options = {
    "All": "",
    "Wingers": ["rw", "lw", "lam", "ram"],
    "Strikers": ["cf", "st","rcf","lcf"],
    "Midfielders": ["cmf", "dmf", "rcmf", "lcmf", "amf","LCMF"],
    "Defenders": ["rb", "cb", "lb", "rcb", "lcb","rwb","lwb"],
}

selected_position = st.sidebar.selectbox("Select Position:", options=list(position_options.keys()))

# Apply position filtering
if selected_position != "All":
    position_filter = filtered_df["Position"].str.contains("|".join(position_options[selected_position]), case=False)
    filtered_df = filtered_df[position_filter.fillna(False)]



# Filter by league
all_leagues = filtered_df["League"].unique()
all_leagues = ['All'] + all_leagues.tolist()
selected_leagues = st.multiselect("Select League:", options=all_leagues, default=["Ligat Haal"])

# Store selected leagues in session state
st.session_state.state['selected_leagues'] = selected_leagues

if "All" in selected_leagues:
    df = filtered_df  # No filtering needed if "All" is selected
else:
    df = filtered_df[filtered_df["League"].isin(selected_leagues)]


# Retrieve or initialize Name and Name2 from session state
Name = st.session_state.state.get('Name')

# Select the Player
player_options = df["Player"].unique().tolist()
Name = st.sidebar.selectbox(
    "Select the Player:",
    options=player_options,
    index=player_options.index(Name) if Name in player_options else 0,
    key='NameSelector',
)

# Store selected player in session state
st.session_state.state['Name'] = Name



# Retrieve or initialize Name and Name2 from session state
selected_leagues = st.session_state.state.get('selected_leagues')

# List of all available parameters
all_params = list(df.columns[7:])

# Filtered parameters based on user selection
selected_params = st.sidebar.multiselect(
    "Select Parameters:",
    options=all_params,
    default=("Key passes per 90", "Dribbles per 90", "Passes to penalty area per 90", "Shot assists per 90", "Crosses per 90", "Shots per 90", "xG per 90")
)  # Default value is all_params (all parameters selected)

params = selected_params
player_league = player_data = df.loc[df['Player'] == Name, "League"].iloc[0]
player_data = df.loc[df['Player'] == Name, selected_params].iloc[0]
values = [math.floor(stats.percentileofscore(df[param], player_data[param])) for param in selected_params]

# Create a table to display the statistic names and values
table_data = {'Statistic': selected_params, 'Value': player_data[selected_params]}
table_df = pd.DataFrame(table_data)
### PRECEPLIE PIZZA

baker = PyPizza(
    params=params,                  # list of parameters
    straight_line_color="#000000",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_lw=1,               # linewidth of last circle
    other_circle_lw=1,              # linewidth for other circles
    other_circle_ls="-."            # linestyle for other circles
)

fig, ax = baker.make_pizza(
    values,              # list of values
    figsize=(8, 8),      # adjust figsize according to your need
    param_location=110,  # where the parameters will be added
    kwargs_slices=dict(
        facecolor="cornflowerblue", edgecolor="#000000",
        zorder=2, linewidth=1
    ),                   # values to be used when plotting slices
    kwargs_params=dict(
        color="#000000", fontsize=8,
        fontproperties=font_normal.prop, va="center"
    ),                   # values to be used when adding parameter
    kwargs_values=dict(
        color="#000000", fontsize=12,
        fontproperties=font_normal.prop, zorder=3,
        bbox=dict(
            edgecolor="#000000", facecolor="cornflowerblue",
            boxstyle="round,pad=0.2", lw=1
        )
    )                    # values to be used when adding parameter-values
)

# Calculate the width and height of the title box
title = f"{Name} Percentile Rank\n{'Compare to all'} {selected_position} {'in'} {'Data Base'}"
title_bbox_props = dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#000000", lw=1)
# Add the title box
fig.text(0.515, 0.97, title, size=18, ha="center", fontproperties=font_bold.prop, color="#000000", bbox=title_bbox_props)



param_value_text = f"{Name}  Values\n"
for param, value in zip(selected_params, player_data):
    param_value_text += f"{param} - {value}\n"

# Adjust the vertical position of the param_value_text box based on the number of parameters
num_params = len(selected_params)
param_value_y = -0.11 - (num_params * 0.015)  # Adjust the value as needed to control the vertical position

# Add the param_value_text box
table_props = dict(facecolor="#cccccc", edgecolor="#000000", lw=1, linestyle="-")
fig.text(0.515, param_value_y, param_value_text, size=12, ha="center", fontproperties=font_normal.prop, weight="bold", color="#000000", bbox=table_props)

# Display the plot
st.pyplot(fig)
