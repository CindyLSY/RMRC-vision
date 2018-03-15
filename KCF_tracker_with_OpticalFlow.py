import numpy as np
import cv2
import time

# display image
def disp(image):
    cv2.imshow(str(np.random.rand()), image)
    cv2.waitKey(10)

def disp_points(image, pts):
    for pt in pts:
        cv2.circle(image, (int(pt[0][0]), int(pt[0][1])), 2, (0, 0, 255), 2)
    disp(image)

# get distance between two points
def get_dist(x, y):
    return np.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)

# a simplified interface to read from video file
def get_frame_from(cap):
    _, frame = cap.read()
    cur_frame = cv2.resize(frame, dsize=(0, 0), fx=0.5, fy=0.5)
    return cur_frame

# do optical flow in a bbox of an image
# rescale the bbox but maintain it inside the image
def rescale_bbox(img_shape, bbox, scale):
    bbox = list(bbox)

    x_lim = img_shape[1]
    y_lim = img_shape[0]

    shift = (scale-1) / 2

    if bbox[0] - shift * bbox[2] >= 0:
        bbox[0] = bbox[0] - shift * bbox[2]
    else:
        bbox[0] = 0

    if bbox[0] + scale * bbox[2] > x_lim:
        bbox[2] = x_lim - bbox[0]
    else:
        bbox[2] = scale * bbox[2]

    if bbox[1] - shift * bbox[3] >= 0:
        bbox[1] = bbox[1] - shift * bbox[3]
    else:
        bbox[1] = 0

    if bbox[1] + shift * bbox[3] > y_lim:
        bbox[3] = y_lim - bbox[1]
    else:
        bbox[3] = scale * bbox[3]

    return tuple(bbox)

# move a bbox by disp, but maintain it within an image
def move_bbox(img_shape, bbox, disp):
    bbox = list(bbox)

    x_lim = img_shape[1]
    y_lim = img_shape[0]

    bbox[0] += disp[0][0]
    bbox[1] += disp[0][1]

    if bbox[0] < 0:
        bbox[0] = 0
    elif bbox[0] > x_lim:
        bbox[0] = x_lim

    if bbox[0] + bbox[2] > x_lim:
        bbox[2] = x_lim - bbox[0]

    if bbox[1] < 0:
        bbox[1] = 0
    elif bbox[1] > y_lim:
        bbox[1] = y_lim

    if bbox[1] + bbox[3] > y_lim:
        bbox[3] = y_lim - bbox[1]

    return tuple(bbox)


# tell if a point is in the bbox
def in_bbox(pt, bbox):
    if pt[0] >= bbox[0] and pt[0] <= bbox[0] + bbox[2] and pt[1] >= bbox[1] and pt[1] <= bbox[1] + bbox[3]:
        return True
    return False

# get feature point only in a region of the image
def get_feature_point_in_bbox(image, bbox, features_params, scale=1):
    # rescale the size of the bbox
    bbox = rescale_bbox(image.shape, bbox, scale)
    # get pts in the bbox of the image
    pts = cv2.goodFeaturesToTrack(image[int(bbox[1]):int(bbox[1]+bbox[3]), int(bbox[0]):int(bbox[0]+bbox[2])], **features_params)
    if pts is None:
        return []
    # shift points back to original coordinate
    shift = np.reshape(np.array(bbox[0:2]), (1, 2))
    return (pts + shift).astype(np.float32)

# get optical flow only in a region of the image
def get_optical_flow_in_bbox(old, cur, bbox, p0, lk_params, scale=1):
    # rescale the size of the bbox
    bbox = rescale_bbox(old.shape, bbox, scale)
    # shift back p0
    shift = np.reshape(np.array(bbox[0:2]), (1, 2))
    p0 = (p0 - shift).astype(np.float32)
    # do optical flow
    old = old[int(bbox[1]):int(bbox[1]+bbox[3]), int(bbox[0]):int(bbox[0]+bbox[2])]
    cur = cur[int(bbox[1]):int(bbox[1]+bbox[3]), int(bbox[0]):int(bbox[0]+bbox[2])]
    p1, st, err = cv2.calcOpticalFlowPyrLK(old, cur, p0, None, **lk_params)

    return (p1 + shift).astype(np.float32), st, err

'''Video Initiation'''
# open the camera for warming up
cap = cv2.VideoCapture('background_shift_slo.MOV')

# grab the first frame
old_frame = get_frame_from(cap)
old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

'''KCF Tracking Initiation'''
# initiate KCF tracker
tracker = cv2.TrackerKCF_create()

# Selecting ROI
bbox = (287, 23, 86, 320)
bbox = cv2.selectROI(old_frame, False)
print(bbox)

# Initialize tracker with first frame and bounding box
ok = tracker.init(old_frame, bbox)

'''OpticalFlow Initiation'''
# params for GoodFeatureToTrack
feature_no = 50
features_params = dict(maxCorners=feature_no, qualityLevel=0.01, minDistance=7, blockSize=7)
# Parameters for LK optical flow
lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
# track the first batch of features
p0 = get_feature_point_in_bbox(old_gray, bbox, features_params, scale=1.25)

# start the tracking
while True:
    # Record FPS
    timer = cv2.getTickCount()

    # read the current frame
    cur_frame = get_frame_from(cap)
    cur_gray = cv2.cvtColor(cur_frame, cv2.COLOR_BGR2GRAY)

    '''using OpticalFlow to track'''
    # replenish if feature points are too few
    if len(p0) < feature_no * 0.8:
        features_params['maxCorners'] = feature_no - len(p0)
        p_new = get_feature_point_in_bbox(cur_gray, bbox, features_params, scale=1.1)
        if not len(p_new) == 0:
            p0 = np.concatenate((p0, p_new), axis=0)
    # do optical flow
    p1, st, err = get_optical_flow_in_bbox(old_gray, cur_gray, bbox, p0, lk_params, scale=2)
    # filter away erroneous points
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
    good_new = good_new[movement < 2 * average_movement]
    good_old = good_old[movement < 2 * average_movement]

    # get final displacement
    displacement = good_new - good_old
    opt_displacement = np.zeros((1, 2))
    for disp in displacement:
        opt_displacement += disp
    if len(displacement) != 0:
        opt_displacement /= len(displacement)

    # plot the optical flow on the frame
    for i, (new, old) in enumerate(zip(good_new, good_old)):
        cv2.line(cur_frame, tuple(new), tuple(old), (0, 255, 0), 1)
        cv2.circle(cur_frame, tuple(new), 2, (0, 255, 0), 2)

    # Now update the previous frame and previous points
    old_gray = cur_gray.copy()
    p0 = good_new.reshape(-1, 1, 2)

    '''using KCF to track'''
    ok, KCF_bbox = tracker.update(cur_frame)

    if ok:
        # Tracking success, draw KCF tracking box
        p1 = (int(KCF_bbox[0]), int(KCF_bbox[1]))
        p2 = (int(KCF_bbox[0] + KCF_bbox[2]), int(KCF_bbox[1] + KCF_bbox[3]))
        cv2.rectangle(cur_frame, p1, p2, (255, 0, 0), 2, 1)
        kcf_displacement = np.array(p1).reshape(1, 2) - np.array([[bbox[0], bbox[1]]])
    else:
        # Tracking failure
        cv2.putText(cur_frame, "Tracking failure detected, switching to Optical Flow", (100, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)
        kcf_displacement = np.array([[0, 0]])

    '''Combine the displacement obtained from KCF and OPT to get a rectified bbox'''
    hybrid_displacement = np.zeros((1, 2))
    if (kcf_displacement == 0).all():
        hybrid_displacement = opt_displacement
    else:
        hybrid_displacement = 0.6 * kcf_displacement + 0.4 * opt_displacement
        bbox = list(bbox)
        bbox[2:] = KCF_bbox[2:]
        bbox = tuple(bbox)
    bbox = move_bbox(cur_frame.shape, bbox, hybrid_displacement)
    # plot the hybrid new bbox
    p1 = (int(bbox[0]), int(bbox[1]))
    p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
    cv2.rectangle(cur_frame, p1, p2, (0, 0, 255), 2, 1)

    '''Show cur frame'''
    # Calculate Frames per second (FPS)
    fps = cv2.getTickFrequency() / (cv2.getTickCount() - timer)
    # Display FPS on frame
    cv2.putText(cur_frame, "FPS : " + str(int(fps)), (100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (50, 170, 50), 2);
    # display cur frame
    cv2.imshow('video', cur_frame)
    # waitkey
    if cv2.waitKey(1) == ord('q'):
        break

