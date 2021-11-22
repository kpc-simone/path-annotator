# visualization.py
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import sys,os

def draw_box(ax,bb):

    # a fancy box with round corners. pad=0.1
    box = mpatches.FancyBboxPatch((bb['xmin'], bb['ymin']),
                             abs(bb['width']), abs(bb['height']),
                             boxstyle="round,pad=0.01",
                             fc=(0.95, 0.95, 0.95),
                             ec=(0.25, 0.25, 0.25))
    ax.add_patch(box)    

arena = {
'xmin'      : -0.150,
'ymin'      : 0,
'width'     : 0.300,
'height'    : 0.500,
}

behavior_colors = {
	'escape'	    : '#279edd',
    'panic'         : '#c97330',
    'freeze'	    : '#27c687',
	'no response'	: '#b3b3b3',
    'mistrial'      : 'white',
	'rear'          : '#fde725',    
    'hide'          : '#675159',
}

def plot_trajectory(xs,ys,outcome):

    fig, axes = plt.subplots(1,1,squeeze=False,figsize=(3,5))
    
    axes[0,0].plot(xs,ys,color=behavior_colors[outcome],linewidth=1.5,alpha=0.5)
    
    for ax in axes.ravel():
        draw_box(ax,arena)
        ax.set_xlim(-0.200,0.200)
        ax.set_ylim(0.550,-0.050)
        shelter = plt.Rectangle((-0.150, 0), 0.160, 0.120,facecolor=behavior_colors['hide'], alpha=0.5)
        ax.add_patch(shelter)
        ax.set_axis_off()    
    
    plt.show()