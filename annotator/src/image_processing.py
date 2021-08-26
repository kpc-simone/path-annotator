# image_processing.py

import numpy as np
import cv2

def generateBackgroundModel(vidcap,pos_0,FPS):
    pos_p = vidcap.get(cv2.CAP_PROP_POS_FRAMES)
    
    vidcap.set(cv2.CAP_PROP_POS_FRAMES,int(pos_0*FPS))
    success,bg_frame = vidcap.read()
    prev_frame = np.float32(bg_frame)
    wa = 0.01 * prev_frame
    wa_mov = prev_frame

    print('generating background model ...')
    while vidcap.isOpened():
        success,frame = vidcap.read()

        if frame is None:
            break
        
        frame = np.float32(frame)
        change = np.absolute(frame - wa_mov)
        
        weighting_factor = 0.1 * ( change.sum().sum().sum() / ( frame.shape[0] * frame.shape[1] * 765) )
        cv2.accumulateWeighted(frame,wa,alpha = weighting_factor)
        cv2.accumulateWeighted(frame,wa_mov,alpha = weighting_factor )
        diff = wa_mov - wa
        diff_metric = diff.mean().mean().mean()
        
        if abs(diff_metric) < 5.0:
            bg_frame = wa
            model_built = True
            
            t_built = vidcap.get(cv2.CAP_PROP_POS_MSEC)/1000
            print('built background model in {} s of video'.format(t_built-pos_0))
            
            # fig, ax = plt.subplots(1,1)
            # ax.imshow(cv2.convertScaleAbs(bg_frame))
            # ax.set_title('Background model generated:')
            # ax.set_axis_off()
            # plt.show(block=False)
            
            break
    vidcap.set(cv2.CAP_PROP_POS_FRAMES,pos_p)
    return bg_frame 

def subGradients(frame, method = 'coarse-blur', k = 641):
    if method == 'coarse-blur':
        blur = cv2.blur(frame,(k,k))
        frz = np.absolute(frame - blur)
        return frz

def maxContrast(frame_blur,bg_blur):
    diff = np.zeros_like( frame_blur ).astype(np.float32)
    for c in range(0,3):
        diff[:,:,c] = (bg_blur[:,:,c] - frame_blur[:,:,c]) / bg_blur[:,:,c]
        diff[:,:,c] = subGradients(diff[:,:,c])
        diff[:,:,c] = np.absolute(( ( diff[:,:,c] - diff[:,:,c].min().min() ) / ( diff[:,:,c].max().max() - diff[:,:,c].min().min() ) ) * 255)
        
    return np.uint8(diff)

def increaseBrightness(frame,factor=5):
    out_frame = np.zeros_like(frame)
    cv2.normalize(frame,out_frame,alpha=0,beta=factor*255,norm_type=cv2.NORM_MINMAX)
    return out_frame
    
def changeRotation(frame,factor=0):
    rotated = frame
    if factor > 0:
        while(factor > 0):
            rotated = cv2.rotate(rotated,cv2.ROTATE_90_CLOCKWISE)
            factor -= 1
    
    elif factor < 0:
        while(factor < 0):
            rotated = cv2.rotate(rotated,cv2.ROTATE_90_COUNTERCLOCKWISE)
            factor += 1
    return rotated
    
    
    
    
    