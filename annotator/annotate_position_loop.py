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
    skip_frames = int(sys.argv[1])
    depth = float(sys.argv[2])
    width = float(sys.argv[3])

sys.path.append(os.path.join(os.path.dirname(__file__),'src'))
from image_processing import *
from visualization import *
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

    trials = asdf['trial'].tolist()
    outcomes = asdf['defensive strategy'].tolist()

    for trial,outcome in zip(trials,outcomes):
        
        if outcome == 'escape':    
            t0 = float(asdf[asdf['trial'] == trial]['run-abs'])
            pos_0 = float(t0 - 0.5)
            pos_f = float(asdf[asdf['trial'] == trial]['hide-abs'] + 1.0)
        elif outcome == 'panic':           
            t0 = float(asdf[asdf['trial'] == trial]['run-abs'])
            pos_0 = float(t0 - 0.5)
            pos_f = float(asdf[asdf['trial'] == trial]['freeze-start-abs'] + 1.0)
        elif outcome == 'freeze':           
            t0 = float(asdf[asdf['trial'] == trial]['shadowON-abs'])
            pos_0 = float(t0 - 0.5)
            pos_f = float(asdf[asdf['trial'] == trial]['shadowOFF-abs'] + 1.0)
        
        vidcap.set(cv2.CAP_PROP_POS_FRAMES,int(pos_0*FPS))
        index = vidcap.get(cv2.CAP_PROP_POS_FRAMES)
        print('skipping to {} trial {} at {}'.format(outcome,trial,vidcap.get(cv2.CAP_PROP_POS_FRAMES)/FPS))
        out_filename = '{}-{}-{}-d{}-t{}-{}'.format(phenotype,sex,animal,day,trial,outcome)
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
                labelPositions(final_frame,transformation_params)
                
                index += skip_frames
                if index < vidcap.get(cv2.CAP_PROP_FRAME_COUNT):
                    vidcap.set(cv2.CAP_PROP_POS_FRAMES, index)
                else:
                    vidcap.release()

        b,a = signal.butter(5,0.5)
        out_data = {
            'n-xpos'      : signal.filtfilt(b,a,np.asarray(n_xsc),padlen=2),
            'n-ypos'      : signal.filtfilt(b,a,np.asarray(n_ysc),padlen=2),
            't-xpos'      : signal.filtfilt(b,a,np.asarray(t_xsc),padlen=2),
            't-ypos'      : signal.filtfilt(b,a,np.asarray(t_ysc),padlen=2),
        }
        ts = np.linspace( pos_0 - t0, pos_f - t0, len(out_data['n-xpos']) )
        out_data['time'] = ts
        
        #for key,values in out_data.items():
        #    print(key,": ",len(values))

        df = pd.DataFrame(data=out_data)        
        df.interpolate(method='linear')
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
        
        print(df.head())
        plot_trajectory(df['n-xpos'],df['n-ypos'],outcome,arenaSize)        
        
        # clear data for next trial
        n_xs.clear()
        n_ys.clear()
        n_xsc.clear()
        n_ysc.clear()
        t_xs.clear()
        t_ys.clear()
        t_xsc.clear()
        t_ysc.clear()
    
    print('completed annotation for all trials in this assay.')
    arenaCorners.clear()
    if input('select another video to annotate? y / [n]') != 'y':
        break