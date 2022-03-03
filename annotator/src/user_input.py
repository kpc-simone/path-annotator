# user_input.py

import numpy as np

lbl_idx = 0
delta_index = 0
skip_frames = 1

clear = np.empty( 300 )
clear[:] = np.NaN
n_xs = np.copy(clear)
n_ys = np.copy(clear)
t_xs = np.copy(clear)
t_ys = np.copy(clear)

n_xsc = np.copy(clear)
n_ysc = np.copy(clear)
t_xsc = np.copy(clear)
t_ysc = np.copy(clear)

NEXT = 9
GO_BACK = 96
SKIP_FRAMES_KEYS = [key for key in np.arange(49,57)]

arenaCorners = []
points_selected = 0 

from image_processing import *
from transformation import *
from msvcrt import getch

from matplotlib import cm

def identifyRotation(frame):
    rotation_factor = 0
    rotated = frame
    print('Use LEFT and RIGHT arrow keys to rotate view 90 degrees (COUNTER)CLOCKWISE')
    print('Press ESC to finalize rotation')    
    while(True):
        #print('ready for input')
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.imshow("frame",rotated)
        cv2.waitKey(1)
        key = ord(getch())
        #print(key)
        if key == 27: #ESC
            print('esc key pressed, exiting program')
            break

        elif key == 224: #Special keys (arrows, f keys, ins, del, etc.)
            continue#key = ord(getch())
        
        elif key == 75: #Left arrow
            rotation_factor -= 1
            print('rotation factor = {}'.format(rotation_factor))
            rotated = cv2.rotate(rotated,cv2.ROTATE_90_COUNTERCLOCKWISE)
            key = 0
        elif key == 77: #Right arrow
            rotation_factor += 1
            print('rotation factor = {}'.format(rotation_factor))
            rotated = cv2.rotate(rotated,cv2.ROTATE_90_CLOCKWISE)      
            key = 0
        cv2.destroyAllWindows()
    return rotation_factor

def selectBrightness(in_frame):
    factor = 1
    print('Use UP and DOWN arrow keys to increase/decrease brightness')
    print('Press ESC to finalize brightness factor selection')    
    while(True):
        frame = increaseBrightness(in_frame,factor)
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.imshow("frame",frame)
        cv2.waitKey(1)
        key = ord(getch())
        if key == 27: #ESC
            print('esc key pressed, exiting program')
            break

        elif key == 224: #Special keys (arrows, f keys, ins, del, etc.)
            continue
            
        elif key == 80: #Down arrow
            factor *= 0.5
            print('factor = {}'.format(factor))
            key = 0
            
        elif key == 72: #Up arrow
            factor += 1
            print('factor = {}'.format(factor))
            key = 0
            
        cv2.destroyAllWindows()
    return factor

def selectPoint(event, x, y, flags, param):

    transformation_params = param
    global lbl_idx
    global points_selected
    global n_xs,n_ys,t_xs,t_ys
    global n_xsc,n_ysc,t_xsc,t_ysc
    
    if points_selected == 0:
        if event == cv2.EVENT_LBUTTONDOWN:
            n_xs[lbl_idx] = int(x)
            n_ys[lbl_idx] = int(y)
            
            # get perspective-distortion correction position
            pc = correctPosition(np.array([[x,y]]),transformation_params)
            n_xsc[lbl_idx] = pc[0]/1000        # convert from mm to m
            n_ysc[lbl_idx] = pc[1]/1000
            points_selected += 1
    
    elif points_selected == 1:        
        if event == cv2.EVENT_LBUTTONDOWN:
            t_xs[lbl_idx] = int(x)
            t_ys[lbl_idx] = int(y)
            
            pc = correctPosition(np.array([[x,y]]),transformation_params)
            t_xsc[lbl_idx] = pc[0]/1000
            t_ysc[lbl_idx] = pc[1]/1000
            
            # reset
            points_selected += 1
            
def get_annotation_corrected():
    global n_xsc,n_ysc,t_xsc,t_ysc
    
    #print('nosepath X in get_annotation_corrected',n_xsc)
    return n_xsc,n_ysc,t_xsc,t_ysc
 
def clear_annotations(size=300):
    
    global n_xs,n_ys,t_xs,t_ys
    global n_xsc,n_ysc,t_xsc,t_ysc
    
    # clear data for next trial
    reset = np.empty( size )
    reset[:] = np.NaN
    
    n_xs = np.copy(reset)
    n_ys = np.copy(reset)
    t_xs = np.copy(reset)
    t_ys = np.copy(reset)
    
    n_xsc = np.copy(reset)
    n_ysc = np.copy(reset)
    t_xsc = np.copy(reset)
    t_ysc = np.copy(reset) 

def reset_playback_control():

    global lbl_idx, skip_frames,delta_index
    lbl_idx = 0
    skip_frames = 1
    delta_index = 0
 
def labelPositions(frame,transformation_params):
    gray = cv2.cvtColor(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
    points_overlay = gray.copy()
    
    global lbl_idx
    if lbl_idx > 0:
        cmap_n = cm.get_cmap('autumn')
        #print(n_xs,n_xs[~np.isnan(n_xs)])
        for idx,(x,y) in enumerate(zip(n_xs[~np.isnan(n_xs)],n_ys[~np.isnan(n_ys)])):
            rgba = cmap_n(idx / len(n_xs[~np.isnan(n_xs)]) )
            color = [ int(c*255) for c in rgba[-2::-1] ]
            cv2.circle(points_overlay,(int(x),int(y)),5,color,-1)
    
        cmap_t = cm.get_cmap('winter')
        for idx,(x,y) in enumerate(zip(t_xs[~np.isnan(t_xs)],t_ys[~np.isnan(t_ys)])):
            rgba = cmap_t(idx / len(t_xs[~np.isnan(t_xs)]) )
            color = [ int(c*255) for c in rgba[-2::-1] ]
            cv2.circle(points_overlay,(int(x),int(y)),5,color,-1)
        
    alpha = 0.5
    gray_overlay = cv2.addWeighted(points_overlay,alpha,gray,1-alpha,gamma=0)
    cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
    
    global points_selected, skip_frames, delta_index
    while(points_selected < 2):
        cv2.imshow("frame",gray_overlay)
        
        input_key = cv2.waitKeyEx(100)

        if input_key == NEXT:
            print('received a next command')
            delta_index = 1
            break
        elif input_key == GO_BACK:
            print('received a go back command')
            delta_index = -2
            break
        elif input_key in SKIP_FRAMES_KEYS:
            print('received a skip frames change key')
            skip_frames = input_key - 48
            break
        
        cv2.setMouseCallback("frame",selectPoint,transformation_params)
        delta_index = 0
        
    lbl_idx_old = lbl_idx
    lbl_idx += delta_index * skip_frames + skip_frames
    # print('old lbl_idx: ', lbl_idx_old, 
            # 'delta_index: ', delta_index,
            # 'skip_frames: ', skip_frames,
            # 'new lbl_idx: ', lbl_idx)
    
    points_selected = 0   
    cv2.destroyAllWindows()   
    return skip_frames,delta_index
    
def selectCorner(event, x, y, flags, param):
    global arenaCorners
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x,",",y)
        
        arenaCorners.append([x,y])
        font = cv2.FONT_HERSHEY_SIMPLEX
        strXY = str(x)+", "+str(y)
    
def selectArenaCorners(frame):
    for corner in ['back left','back right','front right','front left']:
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.imshow("frame",frame)
        print('identify {} corner'.format(corner))
        cv2.setMouseCallback("frame",selectCorner)
        cv2.waitKey(0)
        cv2.destroyAllWindows()    