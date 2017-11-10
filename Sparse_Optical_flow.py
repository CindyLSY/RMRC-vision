import numpy as np
import cv2
from imutils.video import VideoStream
import time


def get_dist(x, y):
    return np.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)


# open the camera for warming up
cap = VideoStream(src=0).start()
# params for ShiTomasi corner detection
features_params = dict(maxCorners=100, qualityLevel=0.01, minDistance=7, blockSize=7)
# Parameters for lucas kanade optical flow
lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
# Take first frame and find corners in it
old_frame = cap.read()
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)
p0 = cv2.goodFeaturesToTrack(old_gray, **features_params)
# wait for the camera to heat up
time.sleep(1)

while True:
    # capture new frame and covert to gray scale
    cur_frame = cap.read()
    cur_gray = cv2.cvtColor(cur_frame, cv2.COLOR_BGR2GRAY)

    # add to feature points if feature points are too few
    if len(p0) <= 80:
        features_params['maxCorners'] = 100 - len(p0)
        p_new = cv2.goodFeaturesToTrack(cur_gray, **features_params)
        p0 = np.concatenate((p0, p_new), axis=0)

    # calculate optical flow
    p1, st, err = cv2.calcOpticalFlowPyrLK(old_gray, cur_gray, p0, None, **lk_params)

    # Select good points
    good_new = p1[st == 1]
    good_old = p0[st == 1]
    # remove steady points
    del_id = []
    for i in range(len(good_new)):
        if get_dist(good_new[i], good_old[i]) <= 2:
            del_id.append(i)
    good_new = np.delete(good_new, del_id, axis=0)
    good_old = np.delete(good_old, del_id, axis=0)
    # remove points that moves too fast
    movement = np.zeros(len(good_new))
    for i in range(len(good_new)):
        movement[i] = get_dist(good_new[i], good_old[i])
    average_movement = movement.mean()
    good_new = good_new[movement < 2 * average_movement + 50]
    good_old = good_old[movement < 2 * average_movement + 50]

    # draw the tracks
    for i, (new, old) in enumerate(zip(good_new, good_old)):
        cv2.line(cur_frame, tuple(new), tuple(old), (0, 255, 0), 1)
        cv2.circle(cur_frame, tuple(new), 5, (0, 255, 0), 3)
    cv2.imshow("frame", cur_frame)
    # Now update the previous frame and previous points
    old_gray = cur_gray.copy()
    p0 = good_new.reshape(-1, 1, 2)

    # waitkey
    if cv2.waitKey(30) == ord('q'):
        break

cv2.destroyAllWindows()
cap.stop()
