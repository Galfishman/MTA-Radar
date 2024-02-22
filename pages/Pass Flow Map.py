import streamlit as st
from matplotlib import rcParams
import matplotlib.pyplot as plt
import pandas as pd
from mplsoccer import Pitch
from scipy.ndimage import gaussian_filter
import matplotlib.patheffects as path_effects
from matplotlib.colorbar import ColorbarBase
from mplsoccer import VerticalPitch

# Set matplotlib parameters
rcParams['text.color'] = '#c7d5cc'  # set the default text color

# Load data
df = pd.read_csv('https://raw.githubusercontent.com/Galfishman/MTA-Radar/main/pages/export.csv')

# Streamlit app
st.title('Passing details plots')

# Sidebar for team selection
TeamPick = st.sidebar.selectbox('Select Team', df['teamFullName'].unique())

# Filter data for the selected team and play type
df_pass = df[(df['teamFullName'] == TeamPick) & (df['playType'] == "Pass") & (df['PassResult'] != 'Incomplete')]

# Convert 'Date' column to datetime format
df_pass['Date'] = pd.to_datetime(df_pass['Date'], errors='coerce')

# Number of recent dates slider in Streamlit
num_recent_dates = st.sidebar.slider('Number of Recent Dates', 1, df_pass['Date'].nunique(), 3)

# Filter data based on the selected number of recent dates
recent_dates = df_pass['Date'].unique()[-num_recent_dates:]
df_pass = df_pass[df_pass['Date'].isin(recent_dates)]


 #####################################################################################################################################################################

# Create pitch object for Gaussian smoothed heatmap
pitch_gaussian = Pitch(pitch_type='opta', line_zorder=2, pitch_color='#22312b', line_color='white')

# Plot Gaussian smoothed heatmap
fig_gaussian, ax_gaussian = pitch_gaussian.draw(figsize=(6.6, 4.125))
fig_gaussian.set_facecolor('#22312b')

# Filter data for the plot
df_pressure = df_pass

# Calculate Gaussian smoothed heatmap
bin_statistic_gaussian = pitch_gaussian.bin_statistic(df_pressure.EventX, df_pressure.EventY, statistic='count', bins=(20, 20))
bin_statistic_gaussian['statistic'] = gaussian_filter(bin_statistic_gaussian['statistic'], 1)
pcm_gaussian = pitch_gaussian.heatmap(bin_statistic_gaussian, ax=ax_gaussian, cmap='hot', edgecolors='black')

# Add the colorbar and format off-white
cbar_gaussian = fig_gaussian.colorbar(pcm_gaussian, ax=ax_gaussian, shrink=0.6)
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
                      pitch_color='#22312b', line_color='white')
# Plot the pass flow map
fig_pass, ax_pass = pitch.draw(figsize=(8, 16))
bin_statistic_pass = pitch.bin_statistic_positional(df_pass.EventX, df_pass.EventY, statistic='count',
                                               positional='full', normalize=True)
pitch.heatmap_positional(bin_statistic_pass, ax=ax_pass, cmap='coolwarm', edgecolors='#22312b')

pitch.scatter(df_pass.EventX, df_pass.EventY, c='white', s=2, ax=ax_pass, alpha = 0.2)

labels = pitch.label_heatmap(bin_statistic_pass, color='white', fontsize=11,
                             ax=ax_pass, ha='center', va='center',
                             str_format='{:0.0%}', path_effects=path_eff)

# Display the pass flow map with custom colormap using Streamlit
st.pyplot(fig_pass)

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



rcParams['figure.dpi'] = 2000


dfmta = df_pass[df_pass['PassResult'] != 'Complete']

passes = dfmta

pass_count = len(dfmta)
rcParams['figure.dpi'] = 2000
plt.style.use('dark_background')

# setup pitch
pitch = Pitch(pitch_type='opta',  line_zorder=2, line_color='white')
# draw
fig_chances, ax_chances = pitch.draw()
bin_statistic = pitch.bin_statistic(dfmta.EventX, dfmta.EventY, statistic='count', bins=(10, 10))
bin_statistic['statistic'] = gaussian_filter(bin_statistic["statistic"], 0)
pcm = pitch.heatmap(bin_statistic, ax=ax_chances, cmap='inferno', edgecolors="black")
cbar = fig.colorbar(pcm, ax=ax_chances, shrink=0.9,location = "left",fraction = 0.95,norm= False)  # Adjust the shrink parameter to change the size



# Plot assists in yellow
assists = passes[passes['PassResult'] == 'Assist']
pitch.arrows(assists['EventX'], assists['EventY'],
             assists['PassEndX'], assists['PassEndY'], width=1,
             headwidth=5, headlength=5,alpha=0.8, color='yellow', ax=ax_chances,zorder=2, label='Assists',facecolor='yellow')

# Plot chances and big chances in blue
chances = passes[passes['PassResult'].isin(['Chance', 'Big Chance'])]
pitch.arrows(chances['EventX'], chances['EventY'],
             chances['PassEndX'], chances['PassEndY'], width=0.7,
             headwidth=5, headlength=5, alpha=0.6, color='white', ax=ax_chances, label='Chances')


ax_chances.legend(facecolor='#22312b', handlelength=3, edgecolor='None', fontsize=8, loc='lower left')

# Set the title
ax_title_chances = ax_chances.set_title(f'Chances Created - {pass_count}', fontsize=30)

# Display the plot using Streamlit
st.pyplot(fig_chances)

 #####################################################################################################################################################################
filtered_df=df_pass[(df_pass['EventX'] >= 5) ]
pass_count2 = len(dfmta)

pitch = Pitch(pitch_type='opta', line_zorder=2, line_color='white')
# draw
fig_xa, ax_xa = pitch.draw()
# Create a 2D histogram with xA values for the filtered data
bin_statistic = pitch.bin_statistic(filtered_df.EventX, filtered_df.EventY, values=filtered_df.xA, statistic='sum', bins=(10, 10))

# Apply Gaussian filter to smooth the heatmap
bin_statistic['statistic'] = gaussian_filter(bin_statistic["statistic"], 1)

# Plot the heatmap with xA values
pcm = pitch.heatmap(bin_statistic, ax=ax_xa, cmap='inferno', edgecolors='#22312b')

# Adding a colorbar

# Overlaying the KDE plot on the VerticalPitch
# Adding a title to the plot with a custom font
title_font = {'fontname': 'Arial', 'color': 'white', 'fontsize': 20}
ax_xa.set_title(f'{TeamPick} xA Heat Map', **title_font)

st.pyplot(fig_xa)

#####################################################################################################################################################################


df_shots = df[(df['teamFullName'] == TeamPick) & ((df['playType'] == "Goal") | (df['playType'] == "Miss") | (df['playType'] == "PenaltyGoal") | (df['playType'] == "Post") | (df['playType'] == "Shot Saved"))]
df_shots['Date'] = pd.to_datetime(df_shots['Date'], errors='coerce')
df_shots = df_shots[df_shots['Date'].isin(recent_dates)]
# Filter for "Goal" and "PenaltyGoal"
df_goals = df[(df['teamFullName'] == TeamPick) & ((df['playType'] == "Goal") | (df['playType'] == "PenaltyGoal"))]

# Filter for "Shot Saved" and "Post"
df_ontarget = df[(df['teamFullName'] == TeamPick) & ((df['playType'] == "Shot Saved") | (df['playType'] == "Post"))]

# Filter for "Miss"
df_miss = df[(df['teamFullName'] == TeamPick) & (df['playType'] == "Miss")]


df_goals = df_shots[df_shots['Date'].isin(recent_dates)]
df_ontarget = df_shots[df_shots['Date'].isin(recent_dates)]
df_miss = df_shots[df_shots['Date'].isin(recent_dates)]


pitch = Pitch(pad_bottom=0.5,  # pitch extends slightly below halfway line
                      pitch_type='opta',
                      half=True,  # half of a pitch
                      goal_type='box',
                      goal_alpha=0.8)  # control the goal transparency


shot_fig, shot_ax = pitch.draw(figsize=(12, 10))
sc_goals = pitch.scatter(df_goals.EventX, df_goals.EventY,
                         s=(df_goals.xG * 900) + 100,
                         c='white',
                         edgecolors='#383838',
                         marker='*',  # You can choose a different marker for goals
                         label='Goals',
                         ax=shot_ax)

# Scatter plot for "Shot Saved" and "Post"
sc_ontarget = pitch.scatter(df_ontarget.EventX, df_ontarget.EventY,
                            s=(df_ontarget.xG * 900) + 100,
                            c='#b94b75',
                            edgecolors='#383838',
                            marker='o',  # You can choose a different marker for on-target shots
                            label='On Target',
                            ax=shot_ax)

# Scatter plot for "Miss"
sc_miss = pitch.scatter(df_miss.EventX, df_miss.EventY,
                        s=(df_miss.xG * 900) + 100,
                        c='#b94b75',
                        edgecolors='#383838',
                        marker='X',
                        label='Misses',
                        ax=shot_ax,
                        alpha = 0.3)

txt = ax.text(x=80, y=80, s='Barcelona shots\nversus Sevilla',
              size=50,
              # here i am using a downloaded font from google fonts instead of passing a fontdict
              va='center', ha='center')
st.pyplot(shot_fig)
