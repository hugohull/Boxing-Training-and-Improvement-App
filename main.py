import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QIntValidator
import cv2
from pydub import AudioSegment
from pydub.playback import play
from punch_tracker import run_punch_tracker  # Make sure punch_tracker is adapted to PyQt

ding = AudioSegment.from_mp3("Audio/Boxing Bell Sound.mp3")


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
        self.current_round = 1
        self.rounds = 12
        self.title = 'Boxing App'
        self.left = 10
        self.top = 10
        self.width = 800
        self.height = 600
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Layouts
        main_layout = QVBoxLayout()
        form_layout = QFormLayout()
        buttons_layout = QHBoxLayout()

        # Widgets
        self.image_label = QLabel(self)
        self.round_input = QLineEdit(self)
        self.work_input = QLineEdit(self)
        self.rest_input = QLineEdit(self)
        self.timer_label = QLabel('00:00', self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 30px; font-weight: bold;")
        self.start_button = QPushButton('Start Timer', self)
        self.start_button.clicked.connect(self.start_timer)
        self.thread = None
        self.start_with_video_button = QPushButton('Start Timer With Video', self)
        self.start_with_video_button.clicked.connect(self.start_timer_and_video)
        self.round_label = QLabel(f'Round {self.current_round:02}/{self.rounds}', self)
        self.round_label.setAlignment(Qt.AlignCenter)
        self.round_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        # Validators
        self.round_validator = QIntValidator(1, 99, self)  # Assuming a reasonable range for rounds is 1 to 99
        self.time_validator = QIntValidator(1, 300, self)  # Assuming a reasonable range for time is 1 to 3600 seconds

        self.round_input.setValidator(self.round_validator)
        self.work_input.setValidator(self.time_validator)
        self.rest_input.setValidator(self.time_validator)

        # Setting placeholders
        # self.round_input.setPlaceholderText("Enter number of rounds.")
        # self.work_input.setPlaceholderText("Enter number of seconds (Work).")
        # self.rest_input.setPlaceholderText("Enter number of seconds (Rest).")
        self.round_input.setText("3")
        self.work_input.setText("30")
        self.rest_input.setText("30")

        # Add the timer label & round label
        main_layout.addWidget(self.timer_label)
        main_layout.addWidget(self.round_label)

        # Form layout for inputs
        form_layout.addRow('Rounds:', self.round_input)
        form_layout.addRow('Work Time (sec):', self.work_input)
        form_layout.addRow('Rest Time (sec):', self.rest_input)

        # Buttons layout
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.start_with_video_button)

        # Adding widgets to main layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.image_label)

        # Set main layout on the application window
        self.setLayout(main_layout)
        self.show()

    def play_sound(self):
        # Using a thread to avoid blocking the GUI while playing sound
        threading.Thread(target=lambda: play(ding), daemon=True).start()

    def update_timer(self):
        if self.seconds_left > 0:
            self.seconds_left -= 1
            timer_str = f"{self.seconds_left // 60:02d}:{self.seconds_left % 60:02d}"
            self.timer_label.setText(timer_str)
        else:
            self.timer.stop()
            if self.current_phase == 'work':
                self.start_rest()
            else:
                self.next_round()

    def start_work(self):
        self.current_phase = 'work'
        self.seconds_left = int(self.work_input.text())
        self.play_sound()
        self.timer.start(1000)
        self.update_round_label()

    def start_rest(self):
        self.current_phase = 'rest'
        self.seconds_left = int(self.rest_input.text())
        self.play_sound()
        self.timer.start(1000)
        self.update_round_label()

    def next_round(self):
        self.rounds -= 1
        if self.rounds > 0:
            self.current_round += 1
            self.start_work()
        else:
            self.play_sound()
            self.timer_label.setText("Done!")
            self.update_round_label()

    def start_timer(self):
        self.rounds = int(self.round_input.text())
        self.start_work()
        self.start_button.setText('Stop Timer')  # Change the button text to 'Stop Timer'
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.stop_timer)
        self.start_with_video_button.hide()
        self.update_round_label()

    def stop_timer(self):
        self.timer.stop()  # Stop the timer
        self.timer_label.setText("Stopped")  # Change the label
        self.start_button.setText('Start Timer')  # Change the button text to 'Start Timer'
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.start_timer)
        self.start_with_video_button.show()
        self.image_label.hide()

    def update_round_label(self):
        # Update the text of round_label to reflect the current state
        self.round_label.setText(f'Round {self.current_round:02}/{self.rounds}')

    @pyqtSlot(QImage)
    def set_image(self, image):
        self.image_label.setPixmap(QPixmap.fromImage(image))

    def start_timer_and_video(self):
        # Start the timer
        self.start_timer()
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
