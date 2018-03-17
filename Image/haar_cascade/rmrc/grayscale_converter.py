import cv2
import os

def convert2gray():        
    for img in os.listdir('negatives'):
        image = cv2.imread('negatives/'+img)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        cv2.imwrite('negatives/'+img, gray)

convert2gray()