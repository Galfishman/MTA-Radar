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
import sklearn
from sklearn.cluster import KMeans
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
st.title('Passing details plots')

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

End_Zone_Display = st.sidebar.checkbox('Display End Zone')
if End_Zone_Display:
    st.write('Plots Shows now the Passes End Zones!')

 #####################################################################################################################################################################

# Create pitch object for Gaussian smoothed heatmap
pitch_gaussian = Pitch(pitch_type='opta', line_zorder=2, pitch_color='black', line_color='white')

# Plot Gaussian smoothed heatmap
fig_gaussian, ax_gaussian = pitch_gaussian.draw(figsize=(6.6, 4.125))
fig_gaussian.set_facecolor('black')

# Filter data for the plot
df_pressure = df_pass

# Calculate Gaussian smoothed heatmap
# Check if the checkbox is checked
if End_Zone_Display:
    bin_statistic_gaussian = pitch_gaussian.bin_statistic(df_pressure.PassEndX, df_pressure.PassEndY, statistic='count', bins=(20, 20))
else:
    # Calculate Gaussian smoothed heatmap using pass origins
    bin_statistic_gaussian = pitch_gaussian.bin_statistic(df_pressure.EventX, df_pressure.EventY, statistic='count', bins=(20, 20))
bin_statistic_gaussian['statistic'] = gaussian_filter(bin_statistic_gaussian['statistic'], 1)
pcm_gaussian = pitch_gaussian.heatmap(bin_statistic_gaussian, ax=ax_gaussian, cmap='hot', edgecolors='black')

# Add the colorbar and format off-white
cbar_gaussian = fig_gaussian.colorbar(pcm_gaussian, ax=ax_gaussian, shrink=0.8)
cbar_gaussian.outline.set_edgecolor('#efefef')
cbar_gaussian.ax.yaxis.set_tick_params(color='#efefef')
ticks_gaussian = plt.setp(plt.getp(cbar_gaussian.ax.axes, 'yticklabels'), color='#efefef')

# Set title for Gaussian smoothed heatmap
ax_title_gaussian = ax_gaussian.set_title(f'{TeamPick} Heat Map', fontsize=16, color='#efefef')

# Display the Gaussian smoothed heatmap using Streamlit
st.pyplot(fig_gaussian)

 #####################################################################################################################################################################



path_eff = [path_effects.Stroke(linewidth=2, foreground='black'),
            path_effects.Normal()]
# setup pitch
pitch = Pitch(pitch_type='opta', line_zorder=2,
                      pitch_color='black', line_color='white')
# Plot the pass flow map
fig_pass, ax_pass = pitch.draw(figsize=(8, 16))
fig_pass.set_facecolor('black')

# Check if the checkbox is checked
if End_Zone_Display:
    # Create a positional bin statistic using pass endpoints
    bin_statistic_pass = pitch.bin_statistic_positional(df_pass.PassEndX, df_pass.PassEndY, statistic='count',
                                                        positional='full', normalize=True)
else:
    # Create a positional bin statistic using pass origins
    bin_statistic_pass = pitch.bin_statistic_positional(df_pass.EventX, df_pass.EventY, statistic='count',
                                                        positional='full', normalize=True)

pitch.heatmap_positional(bin_statistic_pass, ax=ax_pass, cmap='coolwarm', edgecolors='#22312b')

pitch.scatter(df_pass.EventX, df_pass.EventY, c='white', s=2, ax=ax_pass, alpha = 0.2)

labels = pitch.label_heatmap(bin_statistic_pass, color='white', fontsize=11,
                             ax=ax_pass, ha='center', va='center',
                             str_format='{:0.0%}', path_effects=path_eff)

# Display the pass flow map with custom colormap using Streamlit
ax_title = ax_pass.set_title(f'{TeamPick} Passes zones', fontsize=20, pad=10)

st.pyplot(fig_pass)

 
#####################################################################################################################################################################

filtered_df=df_pass[(df_pass['EventX'] >= 5) ]
dfmta = df_pass[(df_pass['PassResult'] != 'Incomplete') | (df_pass['EventY'] > 1) | (df_pass['EventY'] < 100) | (df_pass['xA'] > 0.0001)]

pass_count2 = len(dfmta)

pitch = Pitch(pitch_type='opta', line_zorder=2, line_color='white')
# draw
fig_xa, ax_xa = pitch.draw()
# Create a 2D histogram with xA values for the filtered data
if End_Zone_Display:
    # Create a 2D histogram with xA values for the filtered data using pass endpoints
    bin_statistic = pitch.bin_statistic(dfmta.PassEndX, dfmta.PassEndY, values=dfmta.xA, statistic='sum', bins=(15, 15))
else:
    # Create a 2D histogram with xA values for the filtered data using pass origins
    bin_statistic = pitch.bin_statistic(dfmta.EventX, dfmta.EventY, values=dfmta.xA, statistic='sum', bins=(15, 15))
# Apply Gaussian filter to smooth the heatmap
bin_statistic['statistic'] = gaussian_filter(bin_statistic["statistic"], 1)

# Plot the heatmap with xA values
pcm = pitch.heatmap(bin_statistic, ax=ax_xa, cmap='inferno', edgecolors='#22312b')

# Adding a colorbar
cbar = fig_xa.colorbar(pcm, ax=ax_xa,shrink=0.8)
cbar.set_label('xA', rotation=270, labelpad=15, color='white') # Change text color to white
cbar.ax.tick_params(colors='white') # Change tick text color to white



# Overlaying the KDE plot on the VerticalPitch
# Adding a title to the plot with a custom font
title_font = {'fontname': 'DejaVu Sans', 'color': 'white', 'fontsize': 20}
ax_xa.set_title(f'{TeamPick} xA Heat Map', **title_font)
fig_xa.set_facecolor("black")
ax_xa.set_facecolor("black")



st.pyplot(fig_xa)




#####################################################################################################################################################################


# Create pitch object
pitch = Pitch(pitch_type='opta', line_zorder=2, line_color='black', pitch_color='black',linewidth=4)
bins = (6, 4)

# Plot pass flow map
fig, ax = pitch.draw(figsize=(16, 11), constrained_layout=True, tight_layout=False)
fig.set_facecolor('black')

# plot the heatmap - darker colors = more passes originating from that square
bs_heatmap = pitch.bin_statistic(df_pass.EventX, df_pass.EventY, statistic='count', bins=bins)
hm = pitch.heatmap(bs_heatmap, ax=ax, cmap='Blues')
# plot the pass flow map with a single color ('black') and length of the arrow (5)
fm = pitch.flow(df_pass.EventX, df_pass.EventY, df_pass.PassEndX, df_pass.PassEndY,color='grey',
                arrow_type='average', arrow_length=15, bins=bins, ax=ax)

ax_title = ax.set_title(f'{TeamPick} pass flow map', fontsize=30, pad=-20)



# Display the plot using Streamlit
st.pyplot(fig)

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

title_text = f"{TeamPick} Shots"  # Customize the title as needed
txt = shot_ax.text(0.5, 1, title_text, transform=shot_ax.transAxes, fontsize=20, ha='center',color='Black')
# Text for goal count at the bottom of the plot

goal_count = len(df_goals)  # Count the number of goals
goal_count_text = f"Total Goals: {goal_count}"
# Adjust the y-position (e.g., y=-0.1) to move the text below the pitch. Adjust 'ha' and 'va' for alignment.
txt_goal_count = shot_ax.text(0.5, -0.1, goal_count_text, transform=shot_ax.transAxes, fontsize=12, ha='center', va='top', color='black')

st.pyplot(shot_fig)


 

