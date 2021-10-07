# transformation.py
import numpy as np
import cv2

def getTransformParams(rect,known_dims):
    
    maxWidth, maxHeight = known_dims
    
    # construct the set of destination points to obtain top-down view)
    dst = np.float32([ 
        [int(-maxWidth/2), 0],
        [int(maxWidth/2) - 1, 0],
        [int(maxWidth/2) - 1, int(maxHeight) - 1],
        [int(-maxWidth/2) - 1, int(maxHeight) - 1]])
    
    # compute the perspective transform matrix
    H = cv2.findHomography(rect, dst,cv2.RANSAC,5.0)[0]
    return H
    
def correctPosition(point,H):
    
    point_corrected = np.zeros_like(point)
    point_corrected = np.squeeze(np.squeeze(cv2.perspectiveTransform(np.float32([point]), H),axis=0),axis=0)
    
    return point_corrected