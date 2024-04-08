import os
import random
import threading

import cv2
import numpy as np
import time

from pygame import mixer
from gtts import gTTS

from HistoryManager import *
from utils import play_correct, play_incorrect

# set screen settings
frameWidth = 960
frameHeight = 540

# Line configuration
START = (1000, 0)
END = (1000, 800)
COLOUR = (0, 255, 0)
THICKNESS = 9

# # Webcam video settings
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


def run_punch_tracker(update_gui_func=None, track_punches_flag=lambda: True, flash_screen_callback=None,
                      should_stop=lambda: False):
    load_punch_history()
    # Main program
    while not should_stop():
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
                    if intersects_with_line(x, y, w, h, START, END):
                        if can_detect_again('red'):
                            body_part = "Head" if y + h / 2 < frameHeight / 2 else "Body"
                            punch_history['Total Punches'] += 1
                            punch_history['Total Left'] += 1
                            punch_history[f'Total {body_part}'] += 1
                            punch_history[f'Left {body_part}'] += 1
                            save_punch_history(punch_history)
                            print("Red")
                            if flash_screen_callback is not None:
                                flash_screen_callback('red')
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)

        # Find contours and draw them for blue
        contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_blue:
            area = cv2.contourArea(cnt)
            if area > 400 and track_punches_flag():
                x, y, w, h = cv2.boundingRect(cnt)
                if x > frameWidth / 2:
                    if intersects_with_line(x, y, w, h, START, END):
                        if can_detect_again('blue'):
                            body_part = "Head" if y + h / 2 < frameHeight / 2 else "Body"
                            punch_history['Total Punches'] += 1
                            punch_history['Total Right'] += 1
                            punch_history[f'Total {body_part}'] += 1
                            punch_history[f'Right {body_part}'] += 1
                            save_punch_history(punch_history)
                            print("Blue")
                            if flash_screen_callback is not None:
                                flash_screen_callback('blue')
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 3)

        # Add line
        cv2.line(img, START, END, COLOUR, THICKNESS)

        # Image flipped
        flip_img = cv2.flip(img, 1)

        # If there's a function to update the GUI, call it with the current frame
        if update_gui_func is not None:
            update_gui_func(flip_img)


mixer.init()


# Function to speak the current combination using gTTS
def speak_combination(combination):
    def tts_thread():
        text = ', '.join(combination) + '. Go'
        tts = gTTS(text=text, lang='en')
        temp_file = "temp_combination.mp3"
        tts.save(temp_file)
        mixer.music.load(temp_file)
        mixer.music.play()
        while mixer.music.get_busy():  # Wait for the audio to finish playing
            continue
        os.remove(temp_file)  # Clean up the temporary file

    # Create and start a new thread for the TTS function
    threading.Thread(target=tts_thread).start()


def run_training_mode(update_gui_func=None, track_punches_flag=lambda: True, flash_screen_callback=None,
                      should_stop=lambda: False):
    load_punch_history()

    def generate_random_combination():
        # punches = ['Left Head', 'Left Body', 'Right Head', 'Right Body']
        punches = ['Left Head', 'Left Body']
        num_punches = random.randint(1, 4)  # Generate a random number of punches (1 to 4)
        return [random.choice(punches) for _ in range(num_punches)]

    current_combination = generate_random_combination()
    print(current_combination)
    speak_combination(current_combination)  # Speak the current combination

    detected_punches = []

    while not should_stop():
        success, img = cap.read()
        if not success:
            break

        # Convert to HSV color space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Using the same color ranges for red and blue as in run_punch_tracker
        lower_red1 = np.array([170, 75, 50])
        upper_red1 = np.array([180, 255, 255])
        lower_blue = np.array([85, 50, 40])
        upper_blue = np.array([145, 255, 255])

        # Create masks for red and blue
        mask_red = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)

        # Find contours and draw them for red
        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_red:
            area = cv2.contourArea(cnt)
            if area > 400 and track_punches_flag():
                x, y, w, h = cv2.boundingRect(cnt)
                if x > frameWidth / 2:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)

        # Find contours and draw them for blue
        contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_blue:
            area = cv2.contourArea(cnt)
            if area > 400 and track_punches_flag():
                x, y, w, h = cv2.boundingRect(cnt)
                if x > frameWidth / 2:
                    cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 3)

        # Detect red punches
        contours_red, _ = cv2.findContours(mask_red, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_red:
            area = cv2.contourArea(cnt)
            if area > 400 and track_punches_flag():
                x, y, w, h = cv2.boundingRect(cnt)
                if x > frameWidth / 2 and intersects_with_line(x, y, w, h, START, END) and can_detect_again('red'):
                    body_part = "Head" if y + h / 2 < frameHeight / 2 else "Body"
                    detected_punches.append(f'Left {body_part}')
                    if flash_screen_callback is not None:
                        flash_screen_callback('red')
                    print(detected_punches)

        # Detect blue punches
        contours_blue, _ = cv2.findContours(mask_blue, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours_blue:
            area = cv2.contourArea(cnt)
            if area > 400 and track_punches_flag():
                x, y, w, h = cv2.boundingRect(cnt)
                if x > frameWidth / 2 and intersects_with_line(x, y, w, h, START, END) and can_detect_again('blue'):
                    body_part = "Head" if y + h / 2 < frameHeight / 2 else "Body"
                    detected_punches.append(f'Right {body_part}')
                    if flash_screen_callback is not None:
                        flash_screen_callback('blue')
                    print(detected_punches)

        # Detect if the combination detected is = the set combination
        if track_punches_flag():
            if len(detected_punches) == len(current_combination):
                if detected_punches == current_combination:
                    print("Correct combination thrown")
                    play_correct()
                    current_combination = generate_random_combination()  # Generate a new combination for the next round
                    print(current_combination)  # Print the new combination
                    speak_combination(current_combination)
                    detected_punches = []
                else:
                    print("Try Again")
                    play_incorrect()
                    detected_punches = []

        text = ', '.join(current_combination)  # Convert the combination list to a string
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        thickness = 2
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]

        frame_width = img.shape[1]
        start_x = frame_width - text_size[0] - 10  # 10 pixels from the right edge
        start_y = 50  # Assuming you still want it near the top

        blank_image = np.zeros_like(img)
        cv2.putText(blank_image, text, (start_x, start_y), font, font_scale, (255, 255, 255), thickness)
        flipped_text_image = cv2.flip(blank_image, 1)

        non_zero_indices = np.where(flipped_text_image != [0, 0, 0])
        img[non_zero_indices[0], non_zero_indices[1], :] = flipped_text_image[non_zero_indices[0], non_zero_indices[1],
                                                           :]
        # Add line
        cv2.line(img, START, END, COLOUR, THICKNESS)

        # Update GUI
        if update_gui_func:
            flip_img = cv2.flip(img, 1)
            update_gui_func(flip_img)
