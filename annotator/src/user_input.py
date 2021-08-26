# user_input.py

n_xs = []
n_ys = []
n_xsc = []
n_ysc = []

t_xs = []
t_ys = []
t_xsc = []
t_ysc = []

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
        cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
        cv2.imshow("frame",rotated)
        cv2.waitKey(100)
        key = ord(getch())
        if key == 27: #ESC
            print('esc key pressed, exiting program')
            break

        elif key == 224: #Special keys (arrows, f keys, ins, del, etc.)
            key = ord(getch())
            if key == 75: #Left arrow
                rotation_factor -= 1
                print('rotation factor = {}'.format(rotation_factor))
                rotated = cv2.rotate(rotated,cv2.ROTATE_90_COUNTERCLOCKWISE)
            elif key == 77: #Right arrow
                rotation_factor += 1
                print('rotation factor = {}'.format(rotation_factor))
                rotated = cv2.rotate(rotated,cv2.ROTATE_90_CLOCKWISE)      
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
        cv2.waitKey(100)
        key = ord(getch())
        if key == 27: #ESC
            print('esc key pressed, exiting program')
            break

        elif key == 224: #Special keys (arrows, f keys, ins, del, etc.)
            key = ord(getch())
            if key == 80: #Down arrow
                factor *= 0.5
                print('factor = {}'.format(factor))
            elif key == 72: #Up arrow
                factor += 1
                print('factor = {}'.format(factor))
        cv2.destroyAllWindows()
    return factor

def selectPoint(event, x, y, flags, param):

    transformation_params = param
    global points_selected
    
    if points_selected == 0:
        if event == cv2.EVENT_LBUTTONDOWN:
            
            n_xs.append(x)
            n_ys.append(y)
            
            xc,yc = correctPosition(x,y,transformation_params)
            n_xsc.append(xc)
            n_ysc.append(yc)
            points_selected += 1
    
    elif points_selected == 1:        
        if event == cv2.EVENT_LBUTTONDOWN:
            
            t_xs.append(x)
            t_ys.append(y)
            
            xc,yc = correctPosition(x,y,transformation_params)
            t_xsc.append(xc)
            t_ysc.append(yc)
            
            # reset
            points_selected += 1
  
def labelPositions(frame,transformation_params):
    gray = cv2.cvtColor(cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY),cv2.COLOR_GRAY2BGR)
    points_overlay = gray.copy()
    
    if len(n_xs) > 0:
        cmap_n = cm.get_cmap('autumn')
        for idx,(x,y) in enumerate(zip(n_xs,n_ys)):
            rgba = cmap_n(idx / len(n_xs) )
            color = [ c*255 for c in rgba[-2::-1] ]
            #print('head',color)
            cv2.circle(points_overlay,(x,y),5,color,-1)
    
    if len(t_xs) > 0:
        cmap_t = cm.get_cmap('winter')
        for idx,(x,y) in enumerate(zip(t_xs,t_ys)):
            rgba = cmap_t(idx / len(t_xs) )
            color = [ c*255 for c in rgba[-2::-1] ]
            #print('tail',color)
            cv2.circle(points_overlay,(x,y),5,color,-1)
        
    alpha = 0.5
    gray_overlay = cv2.addWeighted(points_overlay,alpha,gray,1-alpha,gamma=0)
    cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
    
    global points_selected
    while(points_selected < 2):
        cv2.imshow("frame",gray_overlay)
        cv2.setMouseCallback("frame",selectPoint,transformation_params)
        
        # wait for enter key to be pressed
        cv2.waitKey(100)
    points_selected = 0   
    cv2.destroyAllWindows()    
    
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