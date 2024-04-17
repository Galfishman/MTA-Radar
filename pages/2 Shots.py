import streamlit as st
from matplotlib import rcParams
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch
from scipy.ndimage import gaussian_filter
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patheffects as path_effects
from mplsoccer import VerticalPitch, FontManager
from matplotlib.colors import ListedColormap
from matplotlib.colorbar import ColorbarBase
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe
from matplotlib.ticker import MaxNLocator, FuncFormatter
import numpy as np
pd.options.mode.chained_assignment = None  # default='warn'
# Set matplotlib parameters
rcParams['text.color'] = '#c7d5cc'  # set the default text color

# Load data
df = pd.read_csv(
    'https://raw.githubusercontent.com/Galfishman/MTA-Radar/main/export.csv',
    dtype={
        34: str,  # Assuming you want to treat column 34 as string to handle mixed types
        # Add other columns as necessary
    }
)

#  Streamlit app
st.title('Shots details')

# Sidebar for team selection
TeamPick = st.sidebar.selectbox('Select Team', df['teamFullName'].unique())

# Filter data for the selected team and play type
df_pass = df[(df['teamFullName'] == TeamPick) & (df['playType'] == "Pass") & (df['PassResult'] != 'Incomplete')]

# Get unique passers for the selected team
passers = df_pass['Passer'].unique().tolist()

# Add "All" option
passers.insert(0, "All")

# Sidebar for passer selection
PasserPick = st.sidebar.selectbox('Select Player', passers)

# Filter df_pass by selected passer or show all if "All" is selected
if PasserPick != "All":
    df_pass = df_pass[df_pass['toucher'] == PasserPick]

#####################################################################################################################################################################


df_shots = df[(df['teamFullName'] == TeamPick) & ((df['playType'] == "Goal") | (df['playType'] == "Miss") | (df['playType'] == "PenaltyGoal") | (df['playType'] == "Post") | (df['playType'] == "AttemptSaved"))]
#Filter for "Goal" and "PenaltyGoal"
if PasserPick != "All":
    df_shots = df_shots[df_shots['toucher'] == PasserPick]

df_goals = df_shots[(df_shots['teamFullName'] == TeamPick) & ((df_shots['playType'] == "Goal") | (df_shots['playType'] == "PenaltyGoal"))]

# Filter for "Shot Saved" and "Post"
df_ontarget = df_shots[(df_shots['teamFullName'] == TeamPick) & ((df_shots['playType'] == "AttemptSaved") | (df_shots['playType'] == "Post"))]

# Filter for "Miss"
df_miss = df_shots[(df_shots['teamFullName'] == TeamPick) & (df_shots['playType'] == "Miss")]


pitch = VerticalPitch(pad_bottom=0.5,  # pitch extends slightly below halfway line
                      pitch_type='opta',
                      half=True,  # half of a pitch
                      goal_type='box',
                      goal_alpha=0.8)  # control the goal transparency


shot_fig, shot_ax = pitch.draw(figsize=(10, 8))
sc_goals = pitch.scatter(df_goals.EventX, df_goals.EventY,
                         s=(df_goals.xG * 900) + 100,
                         c='white',
                         edgecolors='#383838',
                         marker='*',  # You can choose a different marker for goals
                         label='Goals',
                         ax=shot_ax,
                         zorder = 2)

# Scatter plot for "Shot Saved" and "Post"
sc_ontarget = pitch.scatter(df_ontarget.EventX, df_ontarget.EventY,
                            s=(df_ontarget.xG * 900) + 100,
                            c='blue',
                            edgecolors='white',
                            marker='o',  # You can choose a different marker for on-target shots
                            label='On Target',
                            alpha = 0.8,
                            ax=shot_ax)

# Scatter plot for "Miss"
sc_miss = pitch.scatter(df_miss.EventX, df_miss.EventY,
                        s=(df_miss.xG * 900) + 100,
                        c='grey',
                        edgecolors='white',
                        marker='X',
                        label='Misses',
                        ax=shot_ax,
                        alpha = 0.3)

title_text = f"{PasserPick if PasserPick != 'All' else TeamPick} Shots"
txt = shot_ax.text(0.5, 1, title_text, transform=shot_ax.transAxes, fontsize=20, ha='center', color='Black')

# Text for goal count at the bottom of the plot

goal_count = len(df_goals)  # Count the number of goals
goal_count_text = f"Total Goals: {goal_count}"
# Adjust the y-position (e.g., y=-0.1) to move the text below the pitch. Adjust 'ha' and 'va' for alignment.
# Calculate counts and xG sums
total_shots = len(df_shots)
shots_on_target = len(df_ontarget)
total_xg = df_shots['xG'].sum()

# Adjust the goal count text to include these metrics
goal_count_text = f"Goals: {goal_count}"
shots_text = f"Shots: {total_shots} "
xg_text = f"xG: {total_xg:.2f}"  # formatted to 2 decimal places

# Position and display the metrics on the plot
txt_goal_count = shot_ax.text(0.5, 0.1, f"{goal_count_text}\n{shots_text}\n{xg_text}", transform=shot_ax.transAxes, fontsize=16, ha='center', va='top', color='black')

# Now, display the plot in Streamlit
st.pyplot(shot_fig)



 

