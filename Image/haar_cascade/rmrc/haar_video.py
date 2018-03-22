import cv2

# Use the relevant cascade
cascPath = "data/oxidizer.xml"
Cascade = cv2.CascadeClassifier(cascPath)

video_capture = cv2.VideoCapture(0)
#video_capture = cv2.VideoCapture('http://192.168.0.102:8081')

# Check if camera opened successfully
if (video_capture.isOpened()== False):
    print("Error opening video stream or file")

# Read until video is completed
while(video_capture.isOpened()):
    # Capture frame-by-frame
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    hazard = Cascade.detectMultiScale(gray, 1.3, 10)

    # Draw a rectangle around the hazard sign
    for (x, y, w, h) in hazard:
        if w>100:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()

