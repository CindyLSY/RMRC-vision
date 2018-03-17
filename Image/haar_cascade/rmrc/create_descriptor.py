import cv2
import os

def create_descriptor():        
    for img in os.listdir('negatives'):
        line = 'negatives/'+img+'\n'
        with open('bg.txt','a') as f:
            f.write(line)

create_descriptor()