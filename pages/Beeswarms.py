import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
import math
import matplotlib as mpl
import seaborn as sns
from seaborn import swarmplot
mpl.rcParams['figure.dpi'] = 700
import pickle
from pathlib import Path

###login
# READ DATA
@st.cache_data  # Cache the result of this function
def load_data():
    return pd.read_csv('https://raw.githubusercontent.com/Galfishman/MTA-Radar/main/DataBase.csv')

rawdf = load_data()




st.title("MTA BeeSwarm Compression")

# Create or retrieve session state
if 'state' not in st.session_state:
    st.session_state.state = {'selected_leagues': None, 'Name': None}

st.sidebar.header("Please Filter Here:")

min_selection = st.sidebar.slider('Minutes played:',
                                  min_value=int(rawdf['Minutes played'].min()),
                                  max_value=int(rawdf['Minutes played'].max()),
                                  value=(int(rawdf['Minutes played'].min()), int(rawdf['Minutes played'].max())))
filtered_df = rawdf[(rawdf['Minutes played'] >= min_selection[0]) & (rawdf['Minutes played'] <= min_selection[1])]

# Filter by league
all_leagues = filtered_df["League"].unique().tolist()
selected_leagues = st.selectbox("Select League:", options=all_leagues, index=all_leagues.index(st.session_state.state.get('selected_leagues'), 0))

# Store selected leagues in session state
st.session_state.state['selected_leagues'] = selected_leagues

df = filtered_df[filtered_df["League"].isin([selected_leagues])]

background = '#313332'
text_color ='white'

# Retrieve or initialize Name from session state
Name = st.session_state.state.get('Name')

# Select the Players
player_options = df["Player"].unique().tolist()
Name = st.sidebar.selectbox(
    "Select the First Player:",
    options=player_options,
    index=player_options.index(Name) if Name in player_options else 0,
    key='NameSelector',
)

# Store selected player in session state
st.session_state.state['Name'] = Name

# Select the Second Player
Name2 = st.sidebar.selectbox(
    "Select the Second Player:",
    options=player_options,
    index=player_options.index(Name2) if Name2 in player_options else 0,
    key='NameSelector2',
)

# Retrieve or initialize Name2 from session state
st.session_state.state['Name2'] = Name2

# List of all available parameters
all_params = list(df.columns[7:])

# Filtered parameters based on user selection
selected_params = st.sidebar.multiselect(
    "Select Parameters:",
    options=all_params,
    default=["Key passes per 90", "Dribbles per 90", "Passes to penalty area per 90", "Shot assists per 90", "Crosses per 90", "Shots per 90", "xG per 90", "xA per 90"]
)

# Update the metrics to match the selected parameters
metrics = selected_params

# Calculate the number of subplots needed based on the selected parameters
num_subplots = len(metrics)

# Calculate the number of rows and columns for subplots
num_rows = math.ceil(num_subplots / 2)
num_cols = 2

# Calculate the figure size based on the number of subplots
fig_width = 15
fig_height = 5 + 2.5 * num_rows  # Adjust the value (5) to increase/decrease the height

# Create the figure and subplots
fig, axes = plt.subplots(num_rows, num_cols, figsize=(fig_width, fig_height))
fig.set_facecolor(background)

mpl.rcParams['xtick.color'] = text_color
mpl.rcParams['ytick.color'] = text_color

# Set the common properties for subplots
for ax in axes.flat:
    ax.set_facecolor(background)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)

# Create subplots
for i, metric in enumerate(metrics):
    ax = axes[i // 2, i % 2]
    sns.swarmplot(x=metric, data=df, ax=ax, zorder=1, alpha=0.7)
    ax.scatter(x=df[df['Player'] == Name][metric], y=[0] * len(df[df['Player'] == Name]), s=150, c='yellow', zorder=2, edgecolors='black', alpha=0.9)
    ax.scatter(x=df[df['Player'] == Name2][metric], y=[0] * len(df[df['Player'] == Name2]), s=150, c='white', zorder=2, edgecolors='black', alpha=0.9)
    ax.set_title(metric, color='yellow' if metric == Name else 'white', loc='center', size=13, y=0.89)
    ax.set_xlabel('')
    ax.set_xticklabels([])

# Remove any excess subplots
for j in range(num_subplots, len(metrics)):
    fig.delaxes(axes[j // 2, j % 2])

# Update the title dictionary with players' names
title = {
    'title_name': "●  -  " + Name,
    'title_color': 'yellow',
    'title_name_2': "●  -  " + Name2,
    'title_color_2': 'white',
    'title_fontsize': 16,
}

# Add title text
title_x = fig.subplotpars.left + 0.45
title_y = fig.subplotpars.top + 0.03
title_x_2 = fig.subplotpars.left + 0.3
title_y_2 = fig.subplotpars.top + 0.03

fig.text(title_x, title_y, title['title_name'], fontsize=title['title_fontsize'], color=title['title_color'], ha='center')
fig.text(title_x_2, title_y, title['title_name_2'], fontsize=title['title_fontsize'], color=title['title_color_2'], ha='center')

# Display the plot
st.pyplot(fig)

