import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd
import sys,os
import math

trajectories_folder = '../annotated-paths'
FPS = 20

if __name__ == '__main__':
    phenotype_ = sys.argv[1][2:]
    
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
    
animals = []    
for trajectory_file in os.listdir(trajectories_folder):
    trajectory_info = trajectory_file[:-4].split('-')
    phenotype = trajectory_info[0]
    sex = trajectory_info[1]
    animal = trajectory_info[2]
    
    if phenotype == phenotype_:
        if animal not in animals:
            if sex == 'M':
                animals.insert(0,animal)
            elif sex == 'F':
                animals.append(animal)
#animals.sort()
trials = [t for t in range(1,6)] 
print(animals,trials)

fig, axes = plt.subplots(len(trials),len(animals),squeeze=False,figsize=(len(animals)*2,len(trials)*2))
for a,animal in enumerate(animals):
    for t,trial in enumerate(trials):
        for trajectory_file in os.listdir(trajectories_folder):
            if (animal in trajectory_file) & ('t{}'.format(trial) in trajectory_file):
                tdf = pd.read_csv(os.path.join(trajectories_folder,trajectory_file))
                trajectory_info = trajectory_file[:-4].split('-')
                sex = trajectory_info[1]
                outcome = trajectory_info[5]
                
                axes[t,a].plot(tdf['c-xpos'],tdf['c-ypos'],color=behavior_colors[outcome],linewidth=1.5,alpha=0.5)
        axes[0,a].set_title(sex)
                
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

plt.savefig('figs/all-trial-paths.png', format='png')
plt.show()