from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPen, QColor
from PyQt5.QtWidgets import QLabel


class ImageLabel(QLabel):
    def __init__(self, parent=None):
        super(ImageLabel, self).__init__(parent)
        self.draw_line = False
        self.mode = None
        self.line_offset = -160

    def paintEvent(self, event):
        super(ImageLabel, self).paintEvent(event)
        if self.draw_line:
            painter = QPainter(self)
            pen = QPen(QColor(0, 255, 0), 7)  # Green color, 7px thick
            painter.setPen(pen)

            center_x = self.width() // 2
            line_x = center_x + self.line_offset

            # Draw vertical line
            if self.mode in ["Tracking", "Training"]:
                painter.drawLine(line_x, 0, line_x, self.height())
            elif self.mode == "Competition":
                painter.drawLine(center_x, 0, center_x, self.height())

            mid_height = self.height() // 2

            if self.mode in ["Tracking", "Training"]:
                painter.drawLine(line_x, mid_height, line_x + 50, mid_height)
            elif self.mode == "Competition":
                painter.drawLine(center_x - 50, mid_height, center_x + 50, mid_height)

    def enable_line(self, enable=True, mode=None):
        self.mode = mode
        self.draw_line = enable
        self.update()  # Trigger Repaint
