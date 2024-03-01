import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal, Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
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
        self.title = 'Boxing App'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.rounds = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Layouts
        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        # Widgets
        self.image_label = QLabel(self)
        self.round_input = QLineEdit(self)
        self.round_input.setText("3")
        self.work_input = QLineEdit(self)
        self.work_input.setText("30")
        self.rest_input = QLineEdit(self)
        self.rest_input.setText("30")
        self.timer_label = QLabel('00:00', self)
        self.start_button = QPushButton('Start Timer', self)
        self.start_button.clicked.connect(self.start_timer)
        self.thread = None
        self.start_with_video_button = QPushButton('Start Timer With Video', self)
        self.start_with_video_button.clicked.connect(self.start_timer_and_video)

        # Adding widgets to layouts
        hbox.addWidget(self.round_input)
        hbox.addWidget(self.work_input)
        hbox.addWidget(self.rest_input)
        vbox.addLayout(hbox)
        vbox.addWidget(self.start_button)
        vbox.addWidget(self.start_with_video_button)
        vbox.addWidget(self.timer_label)
        vbox.addWidget(self.image_label)

        self.setLayout(vbox)
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

    def start_rest(self):
        self.current_phase = 'rest'
        self.seconds_left = int(self.rest_input.text())
        self.play_sound()
        self.timer.start(1000)

    def next_round(self):
        self.rounds -= 1
        if self.rounds > 0:
            self.start_work()
        else:
            self.play_sound()
            self.timer_label.setText("Done!")

    def start_timer(self):
        self.rounds = int(self.round_input.text())
        self.start_work()
        self.start_button.setText('Stop Timer')  # Change the button text to 'Stop Timer'
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.stop_timer)
        self.start_with_video_button.hide()

    def stop_timer(self):
        self.timer.stop()  # Stop the timer
        self.timer_label.setText("Stopped")  # Change the label
        self.start_button.setText('Start Timer')  # Change the button text to 'Start Timer'
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.start_timer)
        self.start_with_video_button.show()
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
