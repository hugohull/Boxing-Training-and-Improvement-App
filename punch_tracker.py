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


def run_punch_tracker(update_gui_func=None, track_punches_flag=lambda: True):
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

        # Adjusted Blue color range
        lower_blue = np.array([85, 50, 40])  # Further lower H value and reduce S and V for lighter blues
        upper_blue = np.array([145, 255, 255])  # Further higher H value to include even darker blues

        # Create masks for red and blue
        mask_red = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

        # Find contours and draw them for red
        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_red:
            area = cv2.contourArea(cnt)
            if area > 400:
                x, y, w, h = cv2.boundingRect(cnt)
                if x > frameWidth / 2:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)

        # Find contours and draw them for blue
        contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_blue:
            area = cv2.contourArea(cnt)
            if area > 400:
                x, y, w, h = cv2.boundingRect(cnt)
                if x > frameWidth / 2:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 3)

        # Red detection
        for cnt in contours_red:
            area = cv2.contourArea(cnt)
            if area > 400 and track_punches_flag():
                x, y, w, h = cv2.boundingRect(cnt)
                if x > frameWidth / 2:
                    body_part = "Head" if y + h / 2 < frameHeight / 2 else "Body"
                    if intersects_with_line(x, y, w, h, START, END):
                        if can_detect_again('red'):
                            print(f"Red object. Left {body_part} punch thrown.")
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)

        # Find contours and draw them for blue
        contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_blue:
            area = cv2.contourArea(cnt)
            if area > 400 and track_punches_flag():
                x, y, w, h = cv2.boundingRect(cnt)
                if x > frameWidth / 2:
                    body_part = "Head" if y + h / 2 < frameHeight / 2 else "Body"
                    if intersects_with_line(x, y, w, h, START, END):
                        if can_detect_again('blue'):
                            # Add if statement to filter out body to head border
                            print(f"Blue object. Right {body_part} punch thrown.")
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 3)

        # Add line
        cv2.line(img, START, END, COLOUR, THICKNESS)

        # Image flipped
        flip_img = cv2.flip(img, 1)

        # If there's a function to update the GUI, call it with the current frame
        if update_gui_func is not None:
            update_gui_func(flip_img)

    cap.release()
    cv2.destroyAllWindows()
