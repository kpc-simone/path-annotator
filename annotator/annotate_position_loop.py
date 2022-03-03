# manual_position_annotation.py

from tkinter.filedialog import askopenfilename
from scipy import signal
import pandas as pd
import numpy as np
import progressbar
import cv2 as cv2
import sys,os
import math
import tracemalloc

if __name__ == '__main__':
    timing = sys.argv[1]
    depth = float(sys.argv[2])
    width = float(sys.argv[3])

sys.path.append(os.path.join(os.path.dirname(__file__),'src'))
from image_processing import *
from visualization import *
from incrementing import *
from user_input import *

print('select csv file containing stimulus and behavioral timings')
ktdf = pd.read_csv(askopenfilename())
ktdf = ktdf[ktdf['defensive strategy'] != 'mistrial']
print(ktdf.head())
    
while(True):    
    print('select video for which to annotate paths')
    vidcap = cv2.VideoCapture(askopenfilename(
        filetypes=[('Video Files', '*.avi; *.MP4'), ('All Files', '*.*')]
        )
    )

    # TODO: maybe roll this up into a function that returns a dict
    animal = input('enter animal number: ')
    day = int(input('enter test day: '))
    asdf = ktdf[ktdf['animal'] == animal]
    asdf = asdf[asdf['day'] == day]

    phenotype = asdf['phenotype'].iloc[0]
    sex = asdf['sex'].iloc[0]
    pos_0 = float(asdf['shadowON-abs'].iloc[0])
    
    FPS = vidcap.get(cv2.CAP_PROP_FPS)
    vidcap.set(cv2.CAP_PROP_POS_FRAMES,int(pos_0*FPS))
    success,frame = vidcap.read()

    # select 
    rotation_factor = identifyRotation(frame)
    rotated_frame = changeRotation(frame,rotation_factor)
    brightness_factor = selectBrightness(rotated_frame)
    final_frame = increaseBrightness(rotated_frame,factor=brightness_factor)
    selectArenaCorners(final_frame)

    arenaSize = (width,depth)
    transformation_params = getTransformParams(np.float32([arenaCorners]),arenaSize)

    for index,row in enumerate(asdf.iterrows()):
        
        # TODO add 'timing' argument to pass to get_interval
        t0,pos_0,pos_f,outcome = get_interval(asdf,'trial',index+1,timing=timing)
        
        vidcap.set(cv2.CAP_PROP_POS_FRAMES,int(pos_0*FPS))
        vid_index = vidcap.get(cv2.CAP_PROP_POS_FRAMES)
        print('skipping to {} trial {} at {}'.format(outcome,index+1,vidcap.get(cv2.CAP_PROP_POS_FRAMES)/FPS))
        out_filename = '{}-{}-{}-d{}-t{}-{}'.format(phenotype,sex,animal,day,index+1,outcome)
        
        ts = np.linspace( pos_0 - t0, pos_f - t0, int( (pos_f-pos_0) * FPS + 1) )
        
        clear_annotations(size=len(ts))
        reset_playback_control()
        
        with progressbar.ProgressBar( max_value = pos_f - pos_0 ) as pbar:
            while ( vidcap.get(cv2.CAP_PROP_POS_FRAMES)/FPS < pos_f ):
                try:
                    pbar.update( vidcap.get(cv2.CAP_PROP_POS_FRAMES)/FPS - pos_0 )
                except:
                    pass
                    
                success,frame = vidcap.read()

                if frame is None:
                    break
                
                # increase contrast for viewing
                rotated_frame = changeRotation(frame,rotation_factor)
                final_frame = increaseBrightness(rotated_frame,factor=brightness_factor)
                skip_frames, delta_index = labelPositions(final_frame,transformation_params)
                
                vid_index_old = vid_index
                vid_index += skip_frames + delta_index*skip_frames
                # print('old vid_index: ', vid_index_old, 
                        # 'delta_index: ', delta_index,
                        # 'skip_frames: ', skip_frames,      
                        # 'new vid_index: ', vid_index)
                if vid_index < vidcap.get(cv2.CAP_PROP_FRAME_COUNT):
                    vidcap.set(cv2.CAP_PROP_POS_FRAMES, vid_index)
                else:
                    vidcap.release()

        out_data = {}
        out_data['time'] = ts
        
        n_xsc, n_ysc, t_xsc, t_ysc = get_annotation_corrected()
        #print('nosepath in main script', n_xsc)
        out_data['n-xpos'] = n_xsc
        out_data['n-ypos'] = n_ysc
        out_data['t-xpos'] = t_xsc
        out_data['t-ypos'] = t_ysc
        
        df = pd.DataFrame(data=out_data)        
        df.interpolate(method='linear',inplace=True)
        
        b,a = signal.butter(5,0.5)
        df['n-xpos'] = signal.filtfilt(b,a,df['n-xpos'],padlen=2)
        df['n-ypos'] = signal.filtfilt(b,a,df['n-ypos'],padlen=2)
        df['t-xpos'] = signal.filtfilt(b,a,df['t-xpos'],padlen=2)
        df['t-ypos'] = signal.filtfilt(b,a,df['t-ypos'],padlen=2)

        df['c-xpos'] = ( df['n-xpos'] + df['t-xpos'] ) / 2
        df['c-ypos'] = ( df['n-ypos'] + df['t-ypos'] ) / 2
        df['c-xvel'] = df['c-xpos'].diff() * FPS
        df['c-yvel'] = df['c-ypos'].diff() * FPS
        df['c-xacc'] = df['c-xvel'].diff() * FPS
        df['c-yacc'] = df['c-yvel'].diff() * FPS
        df['c-speed'] = np.sqrt(df['c-yvel']**2+df['c-xvel']**2)
        df['c-scacc'] = np.sqrt(df['c-yacc']**2+df['c-xacc']**2)
        df['a-pos'] = np.degrees(np.arctan( (df['n-ypos'] - df['t-ypos']) / (df['n-xpos'] - df['t-xpos']) ))
        df['a-vel'] = df['a-pos'].diff() * FPS
        
        df.to_csv('../annotated-paths/{}.csv'.format(out_filename))
        
        print(df.head(10))
        print(df.tail(10))
        plot_trajectory(df['n-xpos'],df['n-ypos'],outcome,arenaSize)     
        
        clear_annotations(size=len(ts))
        reset_playback_control()
    
    print('completed annotation for all trials in this assay.')
    arenaCorners.clear()
    if input('select another video to annotate? y / [n]') != 'y':
        break