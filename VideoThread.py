import cv2
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QImage

from punch_tracker import run_punch_tracker, run_training_mode, run_competition_mode


class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    flash_needed = pyqtSignal(str)
    # Define a signal for when a specific punch combination is detected
    combination_detected_signal = pyqtSignal(bool)
    new_combination_signal = pyqtSignal(str)
    update_red_score_signal = pyqtSignal(int)  # Signal to update red score
    update_blue_score_signal = pyqtSignal(int)

    def __init__(self, parent=None, mode='regular'):
        super(VideoThread, self).__init__(parent)
        self.mode = mode
        self._is_running = True
        self.track_punches_flag = lambda: True
        self.tracker_mode_active = False
        self.training_mode_active = False
        self.competition_mode_active = False
        self.cap = None
        self.skill_level = None

    def run(self):

        # Initialize the video capture here
        self._is_running = True

        while self._is_running:
            if self.mode == 'training':
                run_training_mode(
                    update_gui_func=self.update_frame,
                    track_punches_flag=lambda: self.training_mode_active,
                    flash_screen_callback=self.flash_needed.emit,
                    new_combination_callback=self.new_combination_signal.emit,
                    should_stop=lambda: not self._is_running,
                    skill_level=self.skill_level
                )
            elif self.mode == 'competition':
                run_competition_mode(
                    update_gui_func=self.update_frame,
                    track_punches_flag=lambda: self.competition_mode_active,
                    flash_screen_callback=self.flash_needed.emit,
                    new_combination_callback=self.new_combination_signal.emit,
                    red_score_callback= self.update_red_score_signal.emit,
                    blue_score_callback=self.update_blue_score_signal.emit,
                    should_stop=lambda: not self._is_running,
                    skill_level=self.skill_level
                )
            else:
                run_punch_tracker(
                    update_gui_func=self.update_frame,
                    track_punches_flag=lambda: self.tracker_mode_active,
                    flash_screen_callback=self.flash_needed.emit,
                    should_stop=lambda: not self._is_running,
                )

            if not self._is_running:
                break

    def stop(self):
        self.cap.release()
        self._is_running = False

    def update_frame(self, frame):
        # Convert frame to format suitable for QtGui
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(640, 480, aspectRatioMode=Qt.KeepAspectRatio)
        self.change_pixmap_signal.emit(p)
