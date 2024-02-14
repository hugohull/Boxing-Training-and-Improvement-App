# importing the modules
import cv2
import numpy as np
import time

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

# Last detection of colour
last_detection_time = {
    'red': 0,
    'blue': 0
}

# Detection cooldown period
detection_cooldown = 0.5  # Adjust as needed


# Detection check
def can_detect_again(color):
    current_time = time.time()
    if current_time - last_detection_time[color] > detection_cooldown:
        last_detection_time[color] = current_time
        return True
    return False


# Function to check if rectangle intersects with the line
def intersects_with_line(x, y, w, h, line_start, line_end):
    # Create a detection zone around the line
    line_thickness = 10  # You can adjust this based on your line thickness and desired sensitivity
    line_x_min = min(line_start[0], line_end[0]) - line_thickness
    line_x_max = max(line_start[0], line_end[0]) + line_thickness

    # Check if any part of the rectangle is within the detection zone of the line
    if x < line_x_max and x + w > line_x_min:
        return True

    return False

def run_punch_tracker():
    # Main program
    while True:
        success, img = cap.read()
        if not success:
            break

        # Convert to HSV color space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Red color range
        lower_red1 = np.array([170, 75, 50])
        upper_red1 = np.array([180, 255, 255])

        # Blue color range
        lower_blue = np.array([100, 75, 50])
        upper_blue = np.array([120, 255, 255])

        # Create masks for red and blue
        mask_red = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

        # Find contours and draw them for red
        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_red:
            area = cv2.contourArea(cnt)
            if area > 400:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)

        # Find contours and draw them for blue
        contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_blue:
            area = cv2.contourArea(cnt)
            if area > 400:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 3)

        # Red detection
        for cnt in contours_red:
            area = cv2.contourArea(cnt)
            if area > 400:
                x, y, w, h = cv2.boundingRect(cnt)
                if intersects_with_line(x, y, w, h, START, END):
                    if can_detect_again('red'):
                        print("Red object detected (Jab)")
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)

        # Find contours and draw them for blue
        contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_blue:
            area = cv2.contourArea(cnt)
            if area > 400:
                x, y, w, h = cv2.boundingRect(cnt)
                if intersects_with_line(x, y, w, h, START, END):
                    if can_detect_again('blue'):
                        print("Blue object touching the line detected (Backhand)")
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 3)

        # Add line
        cv2.line(img, START, END, COLOUR, THICKNESS)

        # displaying output on Screen
        cv2.imshow("Punch Tracker", img)

        # condition to break programs execution
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
