import numpy as np
import cv2
import sys
import imutils
import os

orig_name = sys.argv[1]
img = cv2.imread(orig_name, 0)
edges = cv2.Canny(img,100,200)
new_name = os.path.splitext(orig_name)[0]
cv2.imwrite("../edged/"+new_name+"_edged.jpg", edges)
