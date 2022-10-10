#!/usr/bin/env python3
# coding:utf-8
"""
algorithms，将source.cpp中的运算改写成函数，以供调用

"""

import cv2 as cv
import numpy as np

def read_img(img_file):
    """"""
    cvimg = cv.imread(img_file)
    
    return cvimg

def edge(cvimg):
    """"""
    grayImage = cv.cvtColor(cvimg, cv.COLOR_BGR2GRAY)
    
    x = cv.Sobel(grayImage, cv.CV_16S, 1, 0)
    y = cv.Sobel(grayImage, cv.CV_16S, 0, 1)

    absX = cv.convertScaleAbs(x)
    absY = cv.convertScaleAbs(y)
    edgeImg = cv.addWeighted(absX, 0.5, absY, 0.5, 0)

    return edgeImg

def binary(cvimg_gray, threshold=30):
    """"""
    ret, img = cv.threshold(cvimg_gray, threshold, 255, cv.THRESH_BINARY)

    return img

def scale_img(cvimg, w, h):
    """w,h - window size"""
    iw = cvimg.shape[1]
    ih = cvimg.shape[0]

    sw = w / iw
    sh = h / ih

    if sw < sh:
        nw = iw * sw
        nh = ih * sw
    else:
        nw = iw * sh
        nh = ih * sh

    simg = cv.resize(cvimg, (int(nw), int(nh)))
    return simg

#  create cube based on edge image
def model3D(edge_img_binary, skin_thickness=0, rotten=False):
    """"""
    cube = None
    
    # colour
    COR_ROTTEN = 64
    COR_SKIN = 192
    COR_SEED = 225
    COR_MEAT = 255

    endPointsSet = []
    endPointsSet_seed = []
    
    if edge_img_binary is not None:
        img = edge_img_binary
        z_max, y_max = img.shape

        if y_max > 0 and z_max > 0:
            x_max = y_max
            cube = np.zeros((z_max, x_max, y_max), dtype='uint8')

            # find endpoints, further center and circle equation
            for z in range(z_max):
                # step 1: img = the right image, based on it
                line = img[z, :]

                # step 2: find end points, remember them
                res =endPoints(line)
                endPointsSet.append(res[0])
                endPointsSet_seed.append(res[1])
            
            # step 3: define circle based on endpoints
            for z in range(len(endPointsSet)):
                cy, r = circle(endPointsSet[z])
                cz = z
                cx = x_max / 2
                
                cy_seed, r_seed = circle(endPointsSet_seed[z])
                
                # step 4:fill new values into cube based on circles
                slice = cube[z, :, :]
                for x in range(slice.shape[0]):
                    for y in range(slice.shape[1]):
                        if x is not None and y is not None and cy is not None and r is not None:
                            if (x - cx)**2 + (y - cy)**2 <= r**2:                                
                                cube[z, x, y] = COR_MEAT
                                # is skin?
                                if skin_thickness > 0:
                                    if skin_thickness >= r:
                                        cube[z, x, y] = COR_SKIN
                                    elif (x - cx)**2 + (y - cy)**2 >= (r - skin_thickness)**2:
                                        cube[z, x, y] = COR_SKIN

                        if x is not None and y is not None and cy_seed is not None and r_seed is not None:
                            if (x - cx)**2 + (y - cy_seed)**2 <= r_seed**2:
                                cube[z, x, y] = COR_SEED

            # add rotten, ball with random position and random radius(>50)
            if rotten:
                r_min = 50
                cx = np.random.randint(20, x_max / 3)
                cy = np.random.randint(20, y_max / 3)
                cz = np.random.randint(20, z_max / 3)
                r = np.random.randint(r_min, x_max / 2)

                for x in range(x_max):
                    for y in range(y_max):
                        for z in range(z_max):
                            if (x - cx)**2 + (y - cy)**2 + (z - cz)**2 <= r**2:
                                if cube[z, x, y] > 0:  # in avocado
                                    cube[z, x, y] = COR_ROTTEN
                
    return cube

def endPoints(line):
    """"""
    lpoint, rpoint = None, None
    lpoint_seed, rpoint_seed = None, None

    # find end points of avocado
    y_max =line.shape[0]
    for i in range(int(y_max * 2 / 3)):
        if line[i] == 255:
            lpoint = i
            break

    for i in range(y_max - 1, int(y_max / 3), -1):
        if line[i] == 255:
            rpoint = i
            break

    # find end points of seed
    cnt_max = 20
    
    # left
    cnt = 0
    lpoint_start_seed = None
    if lpoint is not None and rpoint is not None:
        for i in range(lpoint, int(y_max * 2 / 3)):
            if line[i] == 0:
                cnt += 1
            if cnt >= cnt_max:
                lpoint_start_seed = i  # point E
                break
            elif cnt > 0 and line[i] == 255:  # count again
                cnt = 0

        if lpoint_start_seed is not None:
            for i in range(lpoint_start_seed, int(y_max * 2 / 3)):
                if line[i] == 255:
                    lpoint_seed = i
                    break                    
    
        # right
        cnt = 0
        rpoint_start_seed = None
        for i in range(rpoint, int(y_max / 3), -1):
            if line[i] == 0:
                cnt += 1
            if cnt >= cnt_max:
                rpoint_start_seed = i  # point F
                break
            elif cnt > 0 and line[i] == 255:  # count again
                cnt = 0

        if rpoint_start_seed is not None:
            for i in range(rpoint_start_seed, int(y_max / 3), -1):
                if line[i] == 255:
                    rpoint_seed = i
                    break

    return [lpoint, rpoint], [lpoint_seed, rpoint_seed]

def circle(endpoint):
    """
    endpoint - one group of end points
    """
    center_y, radius = None, None
    if endpoint[0] is not None and endpoint[1] is not None and endpoint[0] < endpoint[1]:
        radius = (endpoint[1] - endpoint[0]) / 2
        center_y = radius + endpoint[0]

    return center_y, radius


                
                

