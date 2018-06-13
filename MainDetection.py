#Motion detection by frame differences and HSV filter
#with trajectory filter installed
#version 1.0
#by Lin Weizhe

import numpy as np
import cv2
import math


def rect2box(rectangles):
    # convert rectangles(x,y,w,h) to boxes(x0,y0,x1,y1)
    boxes = []
    for i in rectangles:
        boxes.append((i[0], i[1], i[0] + i[2], i[1] + i[3]))
    return boxes

def box2rect(boxes):
    # convert boxes(x0,y0,x1,y1) to rectangles(x,y,w,h)
    rectangles=[]
    for i in boxes:
        rectangles.append((i[0],i[1],i[2]-i[0],i[3]-i[1]))
    return rectangles

def getReliableBoxes(boxes1, boxes2):
    # by boxes2, get reliable boxes in boxes1
    reliableBoxes = []
    for box1 in boxes1:
        flag = False
        for box2 in boxes2:
            if mat_inter(extendBox(box1, 0.2), box2):
                reliableBoxes.append(box1)
                flag = True
                break
            if flag: break
    return reliableBoxes


def secondVerification(boxes, trajectory):

    verifiedBoxes=[]
    for box in boxes:
        x0=box[0]
        y0=box[1]
        x1=box[2]
        y1=box[3]
        print(trajectory[y0:y1,x0:x1])
        average=np.sum(trajectory[y0:y1,x0:x1])/((x1-x0)*(y1-y0))
        print (average)
        if average>=128:
            verifiedBoxes.append(box)
    print (len(boxes), len(verifiedBoxes))
    return verifiedBoxes




def extendBox(box, factor):
    # extend box by a factor so that it allows more tolerance
    w = box[2] - box[0]
    h = box[3] - box[1]
    newbox = list(box)
    newbox[0] = int(box[0] - w * factor / 2)
    newbox[2] = int(box[2] + w * factor / 2)
    newbox[1] = int(box[1] - h * factor / 2)
    newbox[3] = int(box[3] + h * factor / 2)

    return newbox


def rectangleFilter(rectangles):
    #rectangles filter: delete full-overlay rectangles
    filteredRectangles = []
    for i in range(len(rectangles)):
        mark = True
        RectA = rectangles[i]
        for j in range(len(rectangles)):
            RectB = rectangles[j]
            if RectA[0] > RectB[0] and RectA[1] > RectB[1] and RectA[0] + RectA[2] < RectB[0] + RectB[2] and RectA[1] + \
                    RectA[3] < RectB[1] + RectB[3]:
                mark = False
                break

        if mark:
            filteredRectangles.append(RectA)
    return filteredRectangles


def mat_inter(box1, box2):
    # check the overlay of the boxes
    # box=(xA,yA,xB,yB)
    x01, y01, x02, y02 = box1
    x11, y11, x12, y12 = box2

    lx = abs((x01 + x02) / 2 - (x11 + x12) / 2)
    ly = abs((y01 + y02) / 2 - (y11 + y12) / 2)
    sax = abs(x01 - x02)
    sbx = abs(x11 - x12)
    say = abs(y01 - y02)
    sby = abs(y11 - y12)
    if lx <= (sax + sbx) / 2 and ly <= (say + sby) / 2:
        return True
    else:
        return False


def solve_coincide(box1, box2):
    # calculate the coincide of two boxes
    # box=(xA,yA,xB,yB)
    #
    if mat_inter(box1, box2) == True:
        x01, y01, x02, y02 = box1
        x11, y11, x12, y12 = box2
        col = min(x02, x12) - max(x01, x11)
        row = min(y02, y12) - max(y01, y11)
        intersection = col * row
        area1 = (x02 - x01) * (y02 - y01)
        area2 = (x12 - x11) * (y12 - y11)
        coincide = intersection / (area1 + area2 - intersection)
        return coincide
    else:
        return False


def getMainDetection(previous_frame, current_frame, satuationThres=46, trajectory=None):

    old_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)

    # Create a mask image for drawing purposes
    mask = np.zeros_like(previous_frame)
    blur = cv2.GaussianBlur(old_gray, (5, 5), 0)
    ret3, old_th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    #situationThres=cv2.getTrackbarPos("situation","controls")

    frame=current_frame
    # convert image to HSV
    imgHSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    # threshold the black out
    imgThres = cv2.inRange(imgHSV, (0, 0, 0), (180, 255, satuationThres))

    # convert image to gray
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Otsu's thresholding after Gaussian filtering
    blur = cv2.GaussianBlur(frame_gray, (5, 5), 0)
    ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # by subtraction, get the difference between two consequent frames
    img = cv2.add(frame, mask)
    img = frame_gray - old_gray
    img1 = th3 - old_th3
    img2 = old_th3 - th3
    img = cv2.add(img1, img2)

    # open and close operation to imgThres
    element = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    opened = cv2.morphologyEx(imgThres, cv2.MORPH_OPEN, element)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, element)

    # open and close operation to img
    img = cv2.morphologyEx(img, cv2.MORPH_OPEN, element)
    img = cv2.morphologyEx(img, cv2.MORPH_CLOSE, element)

    # resize the image by 0.5
    #imgThres = cv2.resize(imgThres, (0, 0), None, 0.5, 0.5)
    #frame = cv2.resize(frame, (0, 0), None, 0.5, 0.5)
    #img = cv2.resize(img, (0, 0), None, 0.5, 0.5)

    # find contours
    image, contours, hierarchy = cv2.findContours(imgThres, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    image2, contours2, hierarchy2 = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    ''' find contour and match rectangles '''
    ''' contours from HSV image '''
    rectangles = []
    for i in range(0, len(contours)):
        x, y, w, h = cv2.boundingRect(contours[i])
        if w >= 5 and h >= 5:
            rectangles.append((x, y, w, h))
            #    cv2.rectangle(frame, (x, y), (x + w, y + h), (160, 32, 240), 2)
    rectangles = rectangleFilter(rectangles)

    #for i in rectangles:
    #    x, y, w, h = i[0], i[1], i[2], i[3]
    #    cv2.rectangle(frame, (x, y), (x + w, y + h), (160, 32, 240), 2)

    ''' contours from frame difference '''
    rectangles2 = []
    for i in range(0, len(contours2)):
        x, y, w, h = cv2.boundingRect(contours2[i])
        if w >= 5 and h >= 5:
            rectangles2.append((x, y, w, h))
            #    cv2.rectangle(frame, (x, y), (x + w, y + h), (160, 32, 240), 2)
    rectangles2 = rectangleFilter(rectangles2)

    #for i in rectangles2:
    #    x, y, w, h = i[0], i[1], i[2], i[3]
    #    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)


    # get reliable boxes
    boxes1 = rect2box(rectangles)
    boxes2 = rect2box(rectangles2)
    reliableBoxes = getReliableBoxes(boxes1, boxes2)

    # 1. if trajectory is none, return reliableBoxes directly without filtering
    # 2. if trajectory isn't none, return filtered reliableBoxes.
    if not(trajectory is None):
        reliableBoxes=secondVerification(reliableBoxes, trajectory)


    return rectangles,rectangles2,box2rect(reliableBoxes)
