import cv2
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage

from punch_tracker import run_punch_tracker


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    flash_needed = pyqtSignal(str)  # Add this line

    def __init__(self, parent=None):
        super(VideoThread, self).__init__(parent)
        self.track_punches_flag = lambda: True

    def run(self):
        self.running = True
        # Modify the following line: no need for flash_screen_callback anymore
        run_punch_tracker(self.update_frame, self.track_punches_flag, self.flash_needed.emit)

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
