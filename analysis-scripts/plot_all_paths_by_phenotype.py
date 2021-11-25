from tkinter.filedialog import askopenfilename
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd
import sys,os
import math

trajectories_folder = '../annotated-paths'
FPS = 20
    
print('select csv file with behavior and stimulus timings')    
ktdf = pd.read_csv(askopenfilename())
ktdf = ktdf[ktdf['defensive strategy'] != 'mistrial']
ktdf = ktdf[ktdf['day'] == 1]
    
def draw_box(ax,bb):

    # a fancy box with round corners. pad=0.1
    box = mpatches.FancyBboxPatch((bb['xmin'], bb['ymin']),
                             abs(bb['width']), abs(bb['height']),
                             boxstyle="round,pad=0.01",
                             fc=(0.95, 0.95, 0.95),
                             ec=(0.25, 0.25, 0.25))
    ax.add_patch(box)    

sys.path.append(os.path.join(os.path.dirname(__file__),'../annotator/src'))
from visualization import behavior_colors
   
fig, axes = plt.subplots(1,2,squeeze=False,figsize = (7,5) )    
for trajectory_file in [f for f in os.listdir(trajectories_folder) if '.csv' in f]:
    tdf = pd.read_csv(os.path.join(trajectories_folder,trajectory_file))
    tdf = tdf[~( ( tdf['n-ypos'] < 0.10) & ( tdf['n-xpos'] < 0.010)) ]
    
    trajectory_info = trajectory_file[:-4].split('-')
    phenotype = trajectory_info[0]
    sex = trajectory_info[1]
    animal = trajectory_info[2]
    day = trajectory_info[3]
    trial = trajectory_info[4][-1]
    outcome = trajectory_info[5]
    trial_df = ktdf[ (ktdf['animal'] == animal) & (ktdf['trial'] == int(trial))]
    #print(trial_df.head())
    
    adf = ktdf[ktdf['animal'] == animal]
    if (len(adf[adf['exclusion rationale'].isnull()]) > 0):
        include = True
    else: 
        include = False
    
    #print(animal,include)
    if include:   
        if phenotype == 'eYFP':
            p = 0    
        
        elif phenotype == 'ChR2':
            p = 1
                
        axes[0,p].scatter(tdf['n-xpos'].iloc[0],tdf['n-ypos'].iloc[0],color=behavior_colors[outcome],s=10,zorder=10)
        axes[0,p].plot(tdf['n-xpos'],tdf['n-ypos'],color=behavior_colors[outcome],linewidth=1.5,alpha=0.5)

axes[0,0].set_title('eYFP')
axes[0,1].set_title('ChR2')

arena = {
'xmin'      : -0.15,
'ymin'      : 0,
'width'     : 0.3,
'height'    : 0.5,
}

for ax in axes.ravel():
    draw_box(ax,arena)
    ax.set_xlim(-0.20,0.20)
    ax.set_ylim(0.55,-0.05)
    shelter = plt.Rectangle((-0.15, 0), 0.160, 0.120,facecolor=behavior_colors['hide'], alpha=0.5)
    ax.add_patch(shelter)
    ax.set_axis_off()    

plt.savefig('figs/paths-byphenotype.png', format='png')
plt.show()