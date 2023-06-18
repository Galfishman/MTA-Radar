import streamlit as st

st.title ("MTA Pizza Compression") 

import pandas as pd
import matplotlib.pyplot as plt
from soccerplots.radar_chart import Radar
from highlight_text import fig_text

from mplsoccer import PyPizza, FontManager

import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 800

#FONT LOAD
font_normal = FontManager(("https://github.com/google/fonts/blob/main/apache/roboto/static/"
                           "Roboto-Regular.ttf?raw=true"))
font_italic = FontManager(("https://github.com/google/fonts/blob/main/apache/roboto/static/"
                           "Roboto-Italic.ttf?raw=true"))
font_bold = FontManager(("https://github.com/google/fonts/blob/main/apache/roboto/static/"
                         "Roboto-Medium.ttf?raw=true"))

#READ DATA
df = pd.read_csv('/Users/galfishman/Desktop/new.csv')


st.dataframe(df)

st.sidebar.header("Please Filter Here:")

Name = st.sidebar.selectbox(
    "Select the Player:",
    options=df["Player"].unique(),
)


# List of all available parameters
all_params = list(df.columns[7:])

# Filtered parameters based on user selection
selected_params = st.sidebar.multiselect(
    "Select Parameters:",
    options=all_params,
    default= ("Key passes per 90","Dribbles per 90","Passes to penalty area per 90","Shot assists per 90", "Crosses per 90", "Shots per 90", "xG per 90"))  # Default value is all_params (all parameters selected)

params = selected_params


#LIST OF VALUES
ranges = []
values = []
values_2 = []
min_range = []
max_range = []


min_range = []
max_range = []

for param in params:
    a = min(df[param])
    b = max(df[param])
    min_range.append(a)
    max_range.append(b)

    
selected_columns = ['Player'] + selected_params

    
for x in range(len(df['Player'])):
    if df['Player'][x] == Name:
        values = df.loc[df['Player'] == Name, selected_columns].values.tolist()[0][1:]



#ALL PIZZA MAKING
# color for the slices and text
num_params = len(selected_params)
slice_colors = ["#1A78CF"] * num_params
text_colors = ["#000000"] * num_params

# instantiate PyPizza class
baker = PyPizza(
    params=params,                  # list of parameters
    min_range=min_range,        # min range values
    max_range=max_range,        # max range values
    background_color="#EBEBE9",     # background color
    straight_line_color="#EBEBE9",  # color for straight lines
    straight_line_lw=1,             # linewidth for straight lines
    last_circle_lw=2,               # linewidth of last circle
    last_circle_color='white',               # linewidth of last circle
    other_circle_lw=0,              # linewidth for other circles
    inner_circle_size=20            # size of inner circle
)

# plot pizza
# Plot pizza
# Plot pizza
fig, ax = baker.make_pizza(
    values,
    figsize=(8, 8.5),
    color_blank_space="same",
    slice_colors=slice_colors,
    value_colors=text_colors,
    value_bck_colors=slice_colors,
    blank_alpha=0.4,
    kwargs_slices=dict(edgecolor="#F2F2F2", zorder=2, linewidth=1),
    kwargs_params=dict(
        color="#000000", fontsize=9, fontproperties=font_normal.prop, va="center"
    ),
    kwargs_values=dict(
        color="#000000",
        fontsize=9,
        fontproperties=font_normal.prop,
        zorder=3,
        bbox=dict(
            edgecolor="#000000",
            facecolor="cornflowerblue",
            boxstyle="round,pad=0.3",
            lw=1,
        ),
    ),
)


#add to title values
League_player = "League"
league_player1 = df.loc[df['Player'] == Name, League_player].values[0]


minutes_name = "Minutes played"
minutes_player1 = df.loc[df['Player'] == Name, minutes_name].values[0]


Position_name = "Position"
Position_name1 = df.loc[df['Player'] == Name, Position_name].values[0]

Team_name = "Team"
team_name1 = df.loc[df['Player'] == Name, Team_name].values[0]


#params_offset = [ True,True,True,False,True,False,True,False,False,
 #               False,False,True,True]

#baker.adjust_texts(params_offset, offset=-0.20)


# add title
fig_text(
    0.06, 1, f"{Name}\n{'Position: ' + Position_name1}\n{'League: '+league_player1 + ' | ' 'Team: ' + team_name1}\n{minutes_player1} Minutes Played",
    size=14, fig=fig,
    ha="left", fontproperties=font_bold.prop, color= 'Black'
)


st.pyplot(fig)
