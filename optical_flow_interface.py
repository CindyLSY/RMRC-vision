import numpy as np
import cv2

# display image
def disp(image):
    cv2.imshow(str(np.random.rand()), image)
    cv2.waitKey(10)

def disp_points(image, pts):
    for pt in pts:
        cv2.circle(image, (int(pt[0]), int(pt[1])), 2, 255, 2)
    disp(image)


# get distance between two points
def get_dist(x, y):
    return np.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)


# a simplified interface to read from video file
def get_frame_from(cap, size=1):
    ret, frame = cap.read()
    if not ret:
        return False
    cur_frame = cv2.resize(frame, dsize=(0, 0), fx=size, fy=size)
    return cur_frame

# do optical flow in a bbox of an image
# rescale the bbox but maintain it inside the image
def rescale_bbox(img_shape, bbox, scale):
    bbox = list(bbox)

    x_lim = img_shape[1]
    y_lim = img_shape[0]

    shift = (scale - 1) / 2

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


# print the bbox
def print_bboxes(frame, bboxes, color='R'):
    if color == 'R':
        color = (0, 0, 255)
    elif color == 'G':
        color = (0, 255, 0)
    elif color == 'B':
        color = (255, 0, 0)
    else:
        color = (255, 255, 255)

    for bbox in bboxes:
        p1 = (int(bbox[0]), int(bbox[1]))
        p2 = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
        cv2.rectangle(frame, p1, p2, color, 2, 1)


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
    pts = cv2.goodFeaturesToTrack(image[int(bbox[1]):int(bbox[1] + bbox[3]), int(bbox[0]):int(bbox[0] + bbox[2])],
                                  **features_params)
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
    old = old[int(bbox[1]):int(bbox[1] + bbox[3]), int(bbox[0]):int(bbox[0] + bbox[2])]
    cur = cur[int(bbox[1]):int(bbox[1] + bbox[3]), int(bbox[0]):int(bbox[0] + bbox[2])]
    p1, st, err = cv2.calcOpticalFlowPyrLK(old, cur, p0, None, **lk_params)

    return (p1 + shift).astype(np.float32), st, err

class OptFlow():
    def __init__(self):
        self.feature_no = 100
        self.features_params = dict(maxCorners=self.feature_no, qualityLevel=0.01, minDistance=7, blockSize=7)
        self.lk_params = dict(winSize=(15, 15), maxLevel=2,
                         criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
        self.initiated = False

    def get_displacement_for_all_bboxes(self, cur_frame, old_frame, bboxes):
        '''converting to gray'''
        cur_gray = cv2.cvtColor(cur_frame, cv2.COLOR_BGR2GRAY)
        old_gray = cv2.cvtColor(old_frame, cv2.COLOR_BGR2GRAY)

        '''using OpticalFlow to track'''
        new_bboxes = []
        for bbox in bboxes:
            displacement = self.get_displacement_for_one_bbox(cur_gray, old_gray, bbox)
            new_bboxes.append((bbox[0]+displacement[0][0], bbox[1]+displacement[0][1], bbox[2], bbox[3]))

        return new_bboxes

    def get_displacement_for_one_bbox(self, cur_gray, old_gray, bbox):
        '''do optical flow and get opt displacement for one bbox'''
        p0 = get_feature_point_in_bbox(old_gray, bbox, self.features_params, scale=1.5)

        print("feature point no.: ", len(p0))
        if len(p0) == 0: # if no point is avilable, return null bbox
            return np.zeros((1, 2))
        # do optical flow
        p1, st, err = get_optical_flow_in_bbox(old_gray, cur_gray, bbox, p0, self.lk_params, scale=2)
        # filter away erroneous points
        good_new = p1[st == 1]
        good_old = p0[st == 1]
        # disp_points(cur_gray, good_old)
        print("good new point no.: ", len(good_new))
        # remove steady points
        del_id = []
        for i in range(len(good_new)):
            if get_dist(good_new[i], good_old[i]) <= 1:
                del_id.append(i)
        good_new = np.delete(good_new, del_id, axis=0)
        good_old = np.delete(good_old, del_id, axis=0)
        # if no point is avilable, return null bbox
        if len(good_new) == 0:
            print("tracking failure")
            return np.zeros((1, 2))
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

        return opt_displacement