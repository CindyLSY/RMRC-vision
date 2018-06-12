from optical_flow_interface import *
from TraceMaker import *
import cv2
from MainDetection import *
import numpy as np

'''Video Initiation'''
# open the camera for warming up
cap = cv2.VideoCapture('demo_video.avi')

# grab the first frame
old_frame = get_frame_from(cap)

# create tracer
trace_maker = TraceMaker(old_frame)

# create tackbar
def nothing(x):
    pass
cv2.imshow('video', old_frame)
cv2.createTrackbar('S', 'video', 0, 255, nothing)
cv2.setTrackbarPos('S','video', 90)


'''Do initial trace finding'''
while True:
    # read the current frame
    cur_frame = get_frame_from(cap)

    # stop when fail to get one frame
    if type(cur_frame) is bool:
        break

    # create backups
    display_frame = np.array(cur_frame)

    '''using Frame Difference to do detection'''
    S = cv2.getTrackbarPos('S', 'video')
    boxes1, boxes2, bboxes = getMainDetection(old_frame, cur_frame, S, None)
    #print (bboxes)
    '''Drawing on the frequency map'''
    trace_maker.update_freq(bboxes)

    '''Draw bbox'''
    print_bboxes(display_frame, bboxes)

trace_maker.enhance_traces()
trace_maker.disp()

'''Video Initiation'''
# open the camera for warming up
cap = cv2.VideoCapture('demo_video.avi')

# grab the first frame
old_frame = get_frame_from(cap)

# create tackbar
def nothing(x):
    pass
cv2.imshow('video', old_frame)
cv2.createTrackbar('S', 'video', 0, 255, nothing)
cv2.setTrackbarPos('S','video', 90)

'''Start actual tracing'''
while True:
    # Record FPS
    timer = cv2.getTickCount()

    # read the current frame
    cur_frame = get_frame_from(cap)

    # stop when fail to get one frame
    if type(cur_frame) is bool:
        break

    # create backups
    display_frame = np.array(cur_frame)

    '''using Frame Difference to do detection'''
    S = cv2.getTrackbarPos('S', 'video')
    boxes1, boxes2, bboxes = getMainDetection(old_frame, cur_frame, S, trace_maker.freq_map)

    '''Drawing on the frequency map'''
    #trace_maker.update_freq(bboxes)

    '''Draw bbox'''
    print_bboxes(display_frame, bboxes)

    '''Show cur frame'''
    # Calculate Frames per second (FPS)
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
    # Display FPS on frame
    cv2.putText(cur_frame, "FPS : " + str(int(fps)), (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);
    # display cur frame
    cv2.imshow('video', display_frame)
    # waitkey for trackbar pause
    a = cv2.waitKey(500)
    if a == ord('q'):
        break
    elif a == ord('z'):
        cv2.waitKey(1000)
