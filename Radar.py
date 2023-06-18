import streamlit as st

st.title ("Try streamlit") 
import pandas as pd
import matplotlib.pyplot as plt
from soccerplots.radar_chart import Radar
from mplsoccer import PyPizza

import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 800

#READ DATA
df = pd.read_csv('https://github.com/Galfishman/MTA-Radar/blob/main/Wing2.csv')


st.dataframe(df)

st.sidebar.header("Please Filter Here:")

Name = st.sidebar.selectbox(
    "Select the Player:",
    options=df["Player"].unique(),
)


# List of all available parameters
all_params = list(df.columns[2:])

# Filtered parameters based on user selection
selected_params = st.sidebar.multiselect(
    "Select Parameters:",
    options=all_params,
    default=None  # Default value is all_params (all parameters selected)
)
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
        color="#000000", fontsize=7, fontproperties=font_normal.prop, va="center"
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

#params_offset = [ True,True,True,False,True,False,True,False,False,
 #               False,False,True,True]

#baker.adjust_texts(params_offset, offset=-0.20)


# add title
fig_text(
    0.515, 1, Name + "  Radar",
    size=16, fig=fig,
    
    ha="center", fontproperties=font_bold.prop, color= 'Black'
)

# add subtitle
fig.text(
    0.515, 0.950,
    "",
    size=15,
    ha="center", fontproperties=font_bold.prop, color="#ffffff"
)


st.pyplot(fig,values)
