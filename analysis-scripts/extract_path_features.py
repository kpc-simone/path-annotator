from tkinter.filedialog import askopenfilename
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from scipy import signal
import pandas as pd
import numpy as np
import sys,os
import math

trajectories_folder = '../annotated-paths'
FPS = 20
    
print('select csv file with behavior and stimulus timings')    
ktdf = pd.read_csv(askopenfilename())
ktdf = ktdf[ktdf['defensive strategy'] != 'mistrial']
ktdf = ktdf[ktdf['day'] == 1]

fdf = pd.DataFrame( columns = ['phenotype','sex','animal','trial','outcome','latency','c-start','c-end','dist-euclid','dist-total','curvature','speed-mean','speed-peak'])
for trajectory_file in os.listdir(trajectories_folder):
    traj_df = pd.read_csv(os.path.join(trajectories_folder,trajectory_file))
        
    trajectory_info = trajectory_file[:-4].split('-')
    phenotype = trajectory_info[0]
    sex = trajectory_info[1]
    animal = trajectory_info[2]
    day = trajectory_info[3]
    trial = int(trajectory_info[4][1:])
    outcome = trajectory_info[5]
    
    if (outcome == 'escape') or (outcome == 'panic'):
        trial_df = ktdf[ (ktdf['animal'] == animal) & (ktdf['trial'] == trial)]
        
        c_start = (traj_df['c-xpos'].iloc[0],traj_df['c-ypos'].iloc[0])
        c_end = (traj_df['c-xpos'].iloc[-1],traj_df['c-ypos'].iloc[-1])
        
        dist_e = np.sqrt( (c_end[0] - c_start[0])**2 + (c_end[1] - c_start[1])**2 )
        dist_t = traj_df['c-speed'].cumsum().max() / FPS
        #print(dist_e)
        
        fdf = fdf.append( {
        'phenotype'     : phenotype,
        'sex'           : sex,
        'animal'        : animal,
        'trial'         : trial,
        'outcome'       : outcome,
        'latency'       : float(trial_df['run-abs']) - float(trial_df['shadowON-abs']),
        'c-start'       : c_start,
        'c-end'         : c_end,
        'dist-euclid'   : dist_e,
        'dist-total'    : dist_t,
        'curvature'     : dist_t / dist_e ,
        'speed-mean'    : traj_df['c-speed'].mean(),
        'speed-peak'    : traj_df['c-speed'].max(),
        'acc-peak'      : traj_df['c-scacc'].max(),
        'xacc-peak'      : traj_df['c-xacc'].max(),
        'yacc-peak'      : traj_df['c-yacc'].max(),
        }, ignore_index = True)

print(fdf.head())    
print(fdf.tail())    

fdf.to_csv('extracts/escape-path-features.csv')