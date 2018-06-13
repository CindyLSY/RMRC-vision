from optical_flow_interface import *
from MainDetection import *
import numpy as np

class TraceMaker():
    '''Try to find the cyclic trace of all possible objects'''
    def __init__(self, frame):
        self.freq_map = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.freq_map[:, :] = 0

    '''Draw the freqency map'''
    def disp(self):
        # display it
        cv2.imshow('map', self.freq_map)
        cv2.waitKey(0)

    '''Update freqency map'''
    def update_freq(self, bboxes):
        for bbox in bboxes:
            self.freq_map[bbox[1]:(bbox[1] + bbox[3]), bbox[0]:(bbox[0] + bbox[3])] += 1

    '''Enhance the traces'''
    def enhance_traces(self):
        # remove less frequent parts
        threshold = np.max(self.freq_map) / 4
        _, self.freq_map = cv2.threshold(self.freq_map, threshold, 255, cv2.THRESH_BINARY)

        # connect the trace
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 10))
        self.freq_map = cv2.morphologyEx(self.freq_map, cv2.MORPH_CLOSE, kernel)

        return self.freq_map
