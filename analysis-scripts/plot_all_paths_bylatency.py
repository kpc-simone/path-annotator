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
   
fig, axes = plt.subplots(2,2,squeeze=False,figsize = (7,10) )    
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
    print(trial_df.head())
    
    if (outcome == 'escape') or (outcome == 'panic'):
        latency = float(trial_df['run-abs']) - float(trial_df['shadowON-abs'])
        
        if phenotype == 'eYFP':
            p = 0    
        
        elif phenotype == 'ChR2':
            p = 1
                
        if latency < 3.0:
           axes[p,0].plot(tdf['n-xpos'],tdf['n-ypos'],color=behavior_colors[outcome],linewidth=1.5,alpha=0.5)
        elif latency > 3.0:
            axes[p,1].plot(tdf['n-xpos'],tdf['n-ypos'],color=behavior_colors[outcome],linewidth=1.5,alpha=0.5)        
        
for ax, row in zip(axes[:,0], ['eYFP', 'ChR2']):
    ax.annotate(row, (0, 1.0), xytext=(-25, 0), ha='right', va='top',
                size=15, rotation=0, xycoords='axes fraction',
                textcoords='offset points')

axes[0,0].set_title('Small')
axes[0,1].set_title('Large')

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

plt.savefig('figs/paths-bylatency.png', format='png')
plt.show()