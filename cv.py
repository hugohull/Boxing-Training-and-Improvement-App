import cv2
import numpy as np

# set screen settings
frameWidth = 960
frameHeight = 540

# Webcam video settings
cap = cv2.VideoCapture(0)
cap.set(3, frameWidth)
cap.set(4, frameHeight)

# Webcam brightness
cap.set(10, 150)

# Main program
while True:
    success, img = cap.read()
    imgResult = img.copy()

    # displaying output on Screen
    cv2.imshow("Punch Tracker", imgResult)

    # condition to break programs execution
    # press q to stop the execution of program
    if cv2.waitKey(1) and 0xFF == ord('q'):
        break
