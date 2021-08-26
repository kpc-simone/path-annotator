import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd
import sys,os
import math

trajectories_folder = '../annotated-paths'
FPS = 20
    
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
    
if __name__ == '__main__':
    phenotype_ = sys.argv[1][2:]
    
if phenotype_ == 'eYFP':
    s_ = 1
elif phenotype_ == 'ChR2':
    s_ = 0
    
fig, axes = plt.subplots(2,3,squeeze=False,figsize = (11,10) ) 
color_bar_set = False   
for trajectory_file in os.listdir(trajectories_folder):
    tdf = pd.read_csv(os.path.join(trajectories_folder,trajectory_file))
    #print(tdf.head())
    #print(trajectory_file)
    
    trajectory_info = trajectory_file[:-4].split('-')
    phenotype = trajectory_info[0]
    sex = trajectory_info[1]
    animal = trajectory_info[2]
    day = trajectory_info[3]
    trial = trajectory_info[4]
    outcome = trajectory_info[5]
    
    if outcome == 'escape':
        a = 0
    elif outcome == 'freeze':
        a = 1
    elif outcome == 'panic':
        a = 2
    
    if sex == 'M':
        s = 0
    elif sex == 'F':
        s = 1

    if phenotype == phenotype_:
        axes[s,a].plot(tdf['c-xpos'],tdf['c-ypos'],color='silver',linewidth=1.5,alpha=0.5)     
        if (s == s_) and (a == 2) and (not color_bar_set):
            im = axes[s,a].scatter(tdf['c-xpos'],tdf['c-ypos'],c=tdf['c-speed'],cmap='plasma',vmin=0,vmax=1.5,zorder=10,s=5)        
            color_bar_set = True
        else:
            axes[s,a].scatter(tdf['c-xpos'],tdf['c-ypos'],c=tdf['c-speed'],cmap='plasma',vmin=0,vmax=1.5,zorder=10,s=5)   

#plt.subplots_adjust(left=-0.005,right=-0.001)
box = axes[0,2].get_position()
pad, width = 0.02, 0.01
cax = fig.add_axes([box.xmax + pad, box.ymin, width, box.height])
ticks = [0,0.25,0.5,0.75,1.0,1.25,1.5]
cbar = fig.colorbar(im, cax=cax,ticks=ticks)         
cbar.set_label('Speed\n(m/s)',va='top',ha='left',rotation=0,in_layout=True)

for ax, row in zip(axes[:,0], ['M', 'F']):
    ax.annotate(row, (0, 0.5), xytext=(-25, 0), ha='left', va='center',
                size=15, rotation=0, xycoords='axes fraction',
                textcoords='offset points')

axes[0,0].set_title('Escape')
axes[0,1].set_title('Freeze')
axes[0,2].set_title('Panic Run')

arena = {
'xmin'      : -0.15,
'ymin'      : 0,
'width'     : 0.3,
'height'    : 0.5,
}

for ax in axes.ravel():
    draw_box(ax,arena)
    ax.set_xlim(-0.15,0.150)
    ax.set_ylim(0.50,-0.00)
    shelter = plt.Rectangle((-0.15, 0), 0.160, 0.120,facecolor=behavior_colors['hide'], alpha=0.5)
    ax.add_patch(shelter)
    ax.set_axis_off()    

plt.savefig('figs/scatter-speeds-bysex.png', format='png')
plt.show()