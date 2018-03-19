import cv2
import time
vidcap = cv2.VideoCapture(0)
success,image = vidcap.read()
count = 0
success = True
while success:
  success,image = vidcap.read()
  print('Read a new frame: ', success)
  cv2.imwrite("./images/rmrc/frame%d.jpg" % count, image)     # save frame as JPEG file
  count += 1
  time.sleep(5)
