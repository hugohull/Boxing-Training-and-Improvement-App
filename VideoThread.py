import cv2
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage

from punch_tracker import run_punch_tracker, run_training_mode


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    flash_needed = pyqtSignal(str)
    # Define a signal for when a specific punch combination is detected
    combination_detected_signal = pyqtSignal(bool)

    def __init__(self, parent=None, mode='regular'):
        super(VideoThread, self).__init__(parent)
        self.mode = mode
        self._is_running = True
        self.track_punches_flag = lambda: True

    def run(self):
        while self._is_running:
            if self.mode == 'training':
                run_training_mode(
                    update_gui_func=self.update_frame,
                    track_punches_flag=self.track_punches_flag,
                    flash_screen_callback=self.flash_needed.emit,
                )
            else:
                run_punch_tracker(self.update_frame, self.track_punches_flag, self.flash_needed.emit)

    def stop(self):
        self._is_running = False

    def update_frame(self, frame):
        # Convert frame to format suitable for QtGui
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, aspectRatioMode=Qt.KeepAspectRatio)
        self.change_pixmap_signal.emit(p)
