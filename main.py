import sys
import threading
import time
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QFormLayout, QMessageBox
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QIntValidator
import cv2
from pydub import AudioSegment
from pydub.playback import play
from punch_tracker import run_punch_tracker

ding = AudioSegment.from_mp3("Audio/Boxing Bell Sound.mp3")

green_button_style = "QPushButton {background-color: #4CAF50; color: white; border-radius: 5px; padding: 6px; font-size: 14px;}" \
               "QPushButton:disabled {background-color: #A5D6A7;}" \
               "QPushButton:hover {background-color: #81C784;}"

red_button_style = "QPushButton {background-color: #D32F2F; color: white; border-radius: 5px; padding: 6px; font-size: 14px;}" \
                   "QPushButton:disabled {background-color: #EF9A9A;}" \
                   "QPushButton:hover {background-color: #E57373;}"

blue_button_style = "QPushButton {background-color: #2196F3; color: white; border-radius: 5px; padding: 6px; font-size: 14px;}" \
                    "QPushButton:disabled {background-color: #BBDEFB;}" \
                    "QPushButton:hover {background-color: #64B5F6;}"


def show_error_message(message):
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setText(f"Error: {message}")
    error_dialog.setWindowTitle("Error")
    error_dialog.setStandardButtons(QMessageBox.Ok)
    error_dialog.exec_()


def play_sound():
    # Using a thread to avoid blocking the GUI while playing sound
    threading.Thread(target=lambda: play(ding), daemon=True).start()


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def run(self):
        self.running = True
        run_punch_tracker(self.update_frame)

    def stop(self):
        self.running = False
        self.wait()

    def update_frame(self, frame):
        # Convert frame to format suitable for QtGui
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, aspectRatioMode=Qt.KeepAspectRatio)
        self.change_pixmap_signal.emit(p)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.pause_button = None
        self.phase_label = None
        self.seconds_left = None
        self.current_phase = None
        self.rest_time_label = None
        self.work_time_label = None
        self.round_input_label = None
        self.thread = None
        self.start_with_video_button = None
        self.start_button = None
        self.rest_input = None
        self.work_input = None
        self.round_input = None
        self.round_label = None
        self.timer_label = None
        self.image_label = None
        self.current_round = 1
        self.rounds = 0
        self.default_round = 12
        self.title = 'Boxing App'
        self.left = 10
        self.top = 10
        self.width = 960
        self.height = 540
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Layouts
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)  # Sets the spacing between widgets in the layout to 10 pixels
        main_layout.setContentsMargins(10, 10, 10, 10)  # Sets the margins of the layout (left, top, right, bottom)

        form_layout = QFormLayout()
        buttons_layout = QHBoxLayout()

        # Labels
        self.image_label = QLabel(self)
        self.timer_label = QLabel('03:00', self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("""
            font-family: 'monaco', monospace;
            font-size: 40px;
            font-weight: bold;
            border-style: solid;
            border-width: 2px;
            border-color: red;
            background-color: #FFC0CB;
            border-radius: 5px;
            padding: 8px;
            margin; auto;
        """)
        self.round_label = QLabel(f'Round {self.current_round:02}/{self.default_round}', self)
        self.round_label.setAlignment(Qt.AlignCenter)
        self.round_label.setStyleSheet("font-size: 34px; font-weight: bold;")
        # Initialize the phase label
        self.phase_label = QLabel('', self)
        self.phase_label.setAlignment(Qt.AlignCenter)
        self.phase_label.setStyleSheet("font-size: 28px; font-weight: bold;")

        # Inputs
        self.round_input = QLineEdit(self)
        self.work_input = QLineEdit(self)
        self.rest_input = QLineEdit(self)

        # Input validators
        self.round_input.setValidator(QIntValidator(0, 99))
        self.rest_input.setValidator(QIntValidator(0, 300))
        self.work_input.setValidator(QIntValidator(0, 300))

        # Buttons
        self.start_button = QPushButton('Start Timer', self)
        self.start_button.setStyleSheet(green_button_style)
        self.start_button.clicked.connect(self.start_timer)
        self.start_with_video_button = QPushButton('Start Timer With Video', self)
        self.start_with_video_button.clicked.connect(self.start_timer_and_video)
        self.start_with_video_button.setStyleSheet(green_button_style)
        self.pause_button = QPushButton('Pause Timer', self)
        self.pause_button.setStyleSheet(blue_button_style)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.hide()

        self.thread = None

        # Setting placeholders
        # self.round_input.setPlaceholderText("Enter number of rounds.")
        # self.work_input.setPlaceholderText("Enter number of seconds (Work).")
        # self.rest_input.setPlaceholderText("Enter number of seconds (Rest).")
        self.round_input.setText("3")
        self.work_input.setText("30")
        self.rest_input.setText("30")

        # Container for buttons
        button_container = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.start_with_video_button)
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.setAlignment(Qt.AlignCenter)
        button_container.setLayout(buttons_layout)

        label_wrapper = QWidget()
        label_wrapper_layout = QVBoxLayout()  # Use QVBoxLayout for vertical centering
        label_wrapper_layout.addWidget(self.timer_label)
        label_wrapper_layout.setAlignment(self.timer_label, Qt.AlignCenter)  # Center the label in the wrapper
        label_wrapper.setLayout(label_wrapper_layout)

        # Add the timer label & round label
        main_layout.addWidget(label_wrapper)
        main_layout.addWidget(self.round_label)
        main_layout.addWidget(self.phase_label)

        # Form layout for inputs
        self.round_input_label = QLabel('Rounds:')
        form_layout.addRow(self.round_input_label, self.round_input)

        self.work_time_label = QLabel('Work Time (sec):')
        form_layout.addRow(self.work_time_label, self.work_input)

        self.rest_time_label = QLabel('Rest Time (sec):')
        form_layout.addRow(self.rest_time_label, self.rest_input)

        # Buttons layout
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.start_with_video_button)

        # Adding widgets to main layout
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_container)
        main_layout.addWidget(self.image_label)

        # Set main layout on the application window
        self.setLayout(main_layout)
        self.show()

    def start_timer(self):
        self.rounds = int(self.round_input.text())
        work_seconds = int(self.work_input.text())
        rest_seconds = int(self.rest_input.text())
        if self.rounds == 0:
            show_error_message("Number of rounds cannot be zero.")
        elif work_seconds == 0:
            show_error_message("Work seconds cannot be zero.")
        elif rest_seconds == 0:
            show_error_message("Rest seconds cannot be zero.")
        else:
            self.default_round = int(self.round_input.text())
            self.start_work()
            self.pause_button.show()
            self.start_button.setText('Stop Timer')  # Change the button text to 'Stop Timer'
            self.start_button.setStyleSheet(red_button_style)
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(self.stop_timer)
            self.start_with_video_button.hide()
            self.update_round_label()

    def start_work(self):
        self.current_phase = 'work'
        self.phase_label.show()
        self.phase_label.setText('Work')  # Update the phase label text
        self.current_phase = 'work'
        self.seconds_left = int(self.work_input.text())
        play_sound()
        self.timer.start(1000)
        self.update_round_label()
        # Hide inputs etc
        self.round_input_label.hide()
        self.round_input.hide()
        self.work_time_label.hide()
        self.work_input.hide()
        self.rest_time_label.hide()
        self.rest_input.hide()

    def start_rest(self):
        self.current_phase = 'rest'
        self.phase_label.setText('Rest')
        self.current_phase = 'rest'
        self.seconds_left = int(self.rest_input.text())
        play_sound()
        self.timer.start(1000)
        self.update_round_label()

    def next_round(self):
        self.rounds -= 1
        if self.rounds > 0:
            self.current_round += 1
            self.start_work()
        else:
            play_sound()
            self.timer_label.setText("Done!")
            self.update_round_label()
            time.sleep(5)
            self.timer_label.setText("00:00")
            self.reset_timer()

    def reset_timer(self):
        self.rounds = 0
        self.current_round = 1
        self.start_button.setText('Start Timer')  # Change the button text to 'Start Timer'
        self.start_button.setStyleSheet(green_button_style)
        self.pause_button.hide()
        self.timer_label.setText('00:00')
        self.round_label.setText('Round 01/12')
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.start_timer)
        self.start_with_video_button.show()
        self.image_label.hide()
        self.phase_label.hide()
        # Show inputs and labels
        self.round_input_label.show()
        self.round_input.show()
        self.work_time_label.show()
        self.work_input.show()
        self.rest_time_label.show()
        self.rest_input.show()

    def update_timer(self):
        if self.seconds_left > 0:
            self.seconds_left -= 1
            timer_str = f"{self.seconds_left // 60:02d}:{self.seconds_left % 60:02d}"
            self.timer_label.setText(timer_str)
            self.timer_label.setAlignment(Qt.AlignCenter)
        else:
            self.timer.stop()
            if self.current_phase == 'work':
                self.start_rest()
            else:
                self.next_round()

    def toggle_pause(self):
        if self.timer.isActive():
            self.timer.stop()
            self.pause_button.setText('Resume Timer')
            self.pause_button.setStyleSheet(green_button_style)  # Optional: Change style if you want to indicate resume
        else:
            self.timer.start(1000)
            self.pause_button.setText('Pause Timer')
            self.pause_button.setStyleSheet(blue_button_style)

    def update_round_label(self):
        # Update the text of round_label to reflect the current state
        self.round_label.setText(f'Round {self.current_round:02}/{self.default_round}')

    def stop_timer(self):
        self.timer.stop()  # Stop the timer
        self.phase_label.setText('Done!')
        self.reset_timer()

    @pyqtSlot(QImage)
    def set_image(self, image):
        self.image_label.setPixmap(QPixmap.fromImage(image))

    def start_timer_and_video(self):
        # Start the timer
        self.start_timer()
        self.phase_label.show()
        # Check if the video thread does not exist or is not running
        if self.thread is None or not self.thread.isRunning():
            # Create and start the thread if it doesn't exist or is not running
            self.thread = VideoThread()
            self.thread.change_pixmap_signal.connect(self.set_image)
            self.thread.start()
        self.image_label.show()
        self.image_label.setAlignment(Qt.AlignCenter)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
