import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from soccerplots.radar_chart import Radar
from highlight_text import fig_text
import numpy as np
from scipy import stats
import math
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

min_selection = st.sidebar.slider('Minutes played:',
                                  min_value=int(rawdf['Minutes played'].min()),
                                  max_value=int(rawdf['Minutes played'].max()),
                                  value=(int(rawdf['Minutes played'].min()), int(rawdf['Minutes played'].max())))

# Create or retrieve session state
if 'state' not in st.session_state:
    st.session_state.state = {'selected_leagues': [], 'selected_player': None}

# Filter by league
all_leagues = rawdf["League"].unique()
all_leagues = ['All'] + all_leagues.tolist()
selected_leagues = st.sidebar.multiselect("Select League:", options=all_leagues, default=st.session_state.state['selected_leagues'])

# Store selected leagues in session state
st.session_state.state['selected_leagues'] = selected_leagues

# Apply league filter
if "All" in selected_leagues:
    filtered_df = rawdf  # No filtering needed if "All" is selected
else:
    filtered_df = rawdf[rawdf["League"].isin(selected_leagues)]

# Apply minutes played filter to the filtered DataFrame
filtered_df = filtered_df[
    (filtered_df['Minutes played'] >= min_selection[0]) & (filtered_df['Minutes played'] <= min_selection[1])
]

st.dataframe(filtered_df)

options = filtered_df["Player"].unique().tolist()
default_idx = options.index(st.session_state.state['selected_player']) if st.session_state.state['selected_player'] in options else 0

Name = st.sidebar.selectbox(
    "Select the Player:",
    options=options,
    index=default_idx
)

# Store selected player in session state
st.session_state.state['selected_player'] = Name

# List of all available parameters
all_params = list(filtered_df.columns[7:])

# Filtered parameters based on user selection
selected_params = st.sidebar.multiselect(
    "Select Parameters:",
    options=all_params,
    default=("Key passes per 90", "Dribbles per 90", "Passes to penalty area per 90", "Shot assists per 90", "Crosses per 90", "Shots per 90", "xG per 90")
)  # Default value is all_params (all parameters selected)

params = selected_params

player_data = filtered_df.loc[filtered_df['Player'] == Name, selected_params].iloc[0]
values = [math.floor(stats.percentileofscore(filtered_df[param], player_data[param])) for param in selected_params]

### PRECEPLIE PIZZA



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

# add title
fig.text(
    0.515, 0.97, f"{Name} Percentile Rank", size=18,
    ha="center", fontproperties=font_bold.prop, color="#000000"
)

# add subtitle
fig.text(
    0.515, 0.942,
    "",
    size=15,

)
st.pyplot(fig)
