# transformation.py

def getTransformParams(points,arena_size):
    
    #correct for perspective distortion
    pts = {
    'back left'     : points[0],
    'back right'    : points[1],
    'front right'   : points[2],
    'front left'    : points[3],
    }
       
    xform = {
    'x0'        : ( (pts['front right'][0] + pts['front left'][0])/2 + (pts['back right'][0] + pts['back left'][0])/2 )/2,
    'ymin'      : (pts['back left'][1] + pts['back right'][1])/2,
    'y0_max'    : ( (pts['front left'][1] - pts['back left'][1]) + (pts['front right'][1] - pts['back right'][1]) )/2,
    'mx1'       : arena_size[0]/(pts['back right'][0] - pts['back left'][0]),
    'mx2'       : arena_size[0]/(pts['front right'][0] - pts['front left'][0]),
    'my'        : arena_size[1]/( ( (pts['front left'][1] - pts['back left'][1]) + (pts['front right'][1] - pts['back right'][1]) )/2 ),    
    }
    
    print('transformation parameters: \n'.format(xform))
    
    return xform
    
def correctPosition(xpos,ypos,xform):
    
    x0 = xform['x0']
    ymin = xform['ymin']
    y0_max = xform['y0_max']
    mx1 = xform['mx1']
    mx2 = xform['mx2']
    my = xform['my']    

    xcorr = (xpos - x0) * (mx2 + (mx1-mx2) * (y0_max-((ypos - ymin)))/y0_max)
    ycorr = (ypos - ymin) * my
    
    return [xcorr,ycorr]