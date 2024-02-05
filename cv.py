# importing the modules
import cv2
import numpy as np

# set screen settings
frameWidth = 960
frameHeight = 540

# Line configuration
START = (1000, 0)
END = (1000, 800)
COLOUR = (0, 255, 0)
THICKNESS = 9

# Webcam video settings
cap = cv2.VideoCapture(0)
cap.set(3, frameWidth)
cap.set(4, frameHeight)

# Webcam brightness
cap.set(10, 150)

# Main program
while True:
    success, img = cap.read()
    if not success:
        break

    # Add line
    cv2.line(img, START, END, COLOUR, THICKNESS)

    # displaying output on Screen
    cv2.imshow("Punch Tracker", img)

    # condition to break programs execution
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()