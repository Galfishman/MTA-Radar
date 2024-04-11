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
    'https://raw.githubusercontent.com/Galfishman/MTA-Radar/main/pages/export.csv',
    dtype={
        34: str,  # Assuming you want to treat column 34 as string to handle mixed types
        # Add other columns as necessary
    }
)

#  Streamlit app
st.title('Passing Clustring')

# Sidebar for team selection
TeamPick = st.sidebar.selectbox('Select Team', df['teamFullName'].unique())

# Filter data for the selected team and play type
df_pass = df[(df['teamFullName'] == TeamPick) & (df['playType'] == "Pass") & (df['PassResult'] != 'Incomplete')]

# Get unique passers for the selected team
passers = df_pass['Passer'].unique().tolist()

# Add "All" option
passers.insert(0, "All")

# Sidebar for passer selection
PasserPick = st.sidebar.selectbox('Select Passer', passers)

# Filter df_pass by selected passer or show all if "All" is selected
if PasserPick != "All":
    df_pass = df_pass[df_pass['Passer'] == PasserPick]




#####################################################################################################################################################################
# Number of clusters
N_clusters = 30

# K-means clustering
X_1 = np.array(df_pass[['EventX', 'EventY', 'PassEndX', 'PassEndY', 'PassAngle', 'PassLength']])
kmeans = KMeans(n_clusters=N_clusters, n_init=10, random_state=0).fit(X_1)
cluster_labels = kmeans.predict(X_1)
df_pass['n_cluster'] = cluster_labels

# Filter passes where PassEndX is higher than 75
df_pass_filtered = df_pass[(df_pass['PassEndX'] > 75) & (df_pass['EventX'] < 100)& (df_pass['EventY'] >= 0)]

# Calculate the number of passes in each cluster for filtered data
pass_counts_filtered = df_pass_filtered['n_cluster'].value_counts()

# Sort the clusters based on the number of passes for filtered data
sorted_clusters_filtered = pass_counts_filtered.sort_values(ascending=False)

# Select the top clusters for filtered data
top_clusters_filtered = sorted_clusters_filtered.head(4)

# Define colors for each cluster
colors = ['black', 'grey', 'yellow', 'white','red','green']

# Create subplots with 2 rows and 2 columns
fig, axes = plt.subplots(2, 2, figsize=(12, 10), dpi=600)

# Plot passes for each cluster on its own pitch for filtered data
for i, (cluster_label, pass_count) in enumerate(top_clusters_filtered.items()):
    passes_in_cluster = df_pass_filtered[df_pass_filtered['n_cluster'] == cluster_label]
    
    # Identify the top 3 passers and receivers for the current cluster
    top_passers = passes_in_cluster['Passer'].value_counts().nlargest(3)
    top_receivers = passes_in_cluster['receiver'].value_counts().nlargest(3)
    
    # Generate strings for top passers and receivers
    top_passers_str = ', '.join([f"{name} ({count})" for name, count in top_passers.items()])
    top_receivers_str = ', '.join([f"{name} ({count})" for name, count in top_receivers.items()])
    
    row = i // 2
    col = i % 2
    pitch = Pitch(pitch_type='opta', line_zorder=2, pitch_color='#22312b', line_color='white')
    pitch.draw(ax=axes[row, col])
    axes[row, col].scatter(
        passes_in_cluster['EventX'], passes_in_cluster['EventY'], color=colors[i], zorder=2, s=1
    )
    pitch.arrows(
        passes_in_cluster['EventX'], passes_in_cluster['EventY'],
        passes_in_cluster['PassEndX'], passes_in_cluster['PassEndY'],
        ax=axes[row, col], width=0.9, headwidth=10, headlength=15, alpha=0.5, color=colors[i], zorder=2,
    )
    axes[row, col].set_title(f'Cluster {cluster_label} (Rank: {i+1}) - {pass_count} passes\nTop 3 Passers: {top_passers_str}\nTop 3 Receivers: {top_receivers_str}')

# Add title and legend
fig.suptitle(f'{TeamPick} Most Common Passes To Final Third Cluster', fontsize=16,color='white')
plt.tight_layout()
fig.set_facecolor('black')

# Display the plot using Streamlit
st.pyplot(fig)


 #####################################################################################################################################################################
 #####################################################################################################################################################################
# Filter passes ending inside the box
box_passes = df_pass[(df_pass['PassEndX'] >= 84) & 
                     (df_pass['PassEndX'] <= 100) & 
                     (df_pass['PassEndY'] >= 21) & 
                     (df_pass['PassEndY'] <= 79) &
                     (df_pass['EventX'] < 100)]

# Number of clusters for passes ending inside the box
N_clusters_box = 10

# K-means clustering for passes ending inside the box
X_box = np.array(box_passes[['EventX', 'EventY', 'PassEndX', 'PassEndY', 'PassAngle', 'PassLength']])
kmeans_box = KMeans(n_clusters=N_clusters_box, n_init=10, random_state=0).fit(X_box)
cluster_labels_box = kmeans_box.predict(X_box)
box_passes['n_cluster'] = cluster_labels_box

# Calculate the number of passes in each cluster for passes ending inside the box
pass_counts_box = box_passes['n_cluster'].value_counts()

# Sort the clusters based on the number of passes for passes ending inside the box
sorted_clusters_box = pass_counts_box.sort_values(ascending=False)

# Select the top clusters for passes ending inside the box
top_clusters_box = sorted_clusters_box.head(4)

# Create subplots with 2 rows and 2 columns for passes ending inside the box
fig_box, axes_box = plt.subplots(2, 2, figsize=(12, 10), dpi=600)

# Plot passes for each cluster on its own pitch for passes ending inside the box
for i, (cluster_label, pass_count) in enumerate(top_clusters_box.items()):
    passes_in_cluster_box = box_passes[box_passes['n_cluster'] == cluster_label]
    
    # Identify the top 3 passers and receivers for the current cluster
    top_passers_box = passes_in_cluster_box['Passer'].value_counts().nlargest(3)
    top_receivers_box = passes_in_cluster_box['receiver'].value_counts().nlargest(3)
    
    # Generate strings for top passers and receivers
    top_passers_str_box = ', '.join([f"{name} ({count})" for name, count in top_passers_box.items()])
    top_receivers_str_box = ', '.join([f"{name} ({count})" for name, count in top_receivers_box.items()])
    
    row_box = i // 2
    col_box = i % 2
    pitch_box = Pitch(pitch_type='opta', line_zorder=2, pitch_color='#22312b', line_color='white')
    pitch_box.draw(ax=axes_box[row_box, col_box])
    axes_box[row_box, col_box].scatter(
        passes_in_cluster_box['EventX'], passes_in_cluster_box['EventY'], color=colors[i], zorder=2, s=1
    )
    pitch_box.arrows(
        passes_in_cluster_box['EventX'], passes_in_cluster_box['EventY'],
        passes_in_cluster_box['PassEndX'], passes_in_cluster_box['PassEndY'],
        ax=axes_box[row_box, col_box], width=0.9, headwidth=10, headlength=15, alpha=0.5, color=colors[i], zorder=2,
    )
    axes_box[row_box, col_box].set_title(f'Cluster {cluster_label} (Rank: {i+1}) - {pass_count} passes\nTop 3 Passers: {top_passers_str_box}\nTop 3 Receivers: {top_receivers_str_box}', color='white')

# Add title and legend for passes ending inside the box
fig_box.suptitle(f'{TeamPick} Most Common Passes to Box Cluster', fontsize=16, color='white')
plt.tight_layout()
fig_box.set_facecolor('black')

# Display the plot for passes ending inside the box using Streamlit
st.pyplot(fig_box)
