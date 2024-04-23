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
            if self.mode == "Competition":
                painter = QPainter(self)
                pen = QPen(QColor(0, 255, 0), 7)
                painter.setPen(pen)
                painter.drawLine(self.width() // 2, 0, self.width() // 2, self.height())
            elif self.mode == "Tracking" or self.mode == "Training":
                center_x = self.width() // 2
                line_x = center_x + self.line_offset
                painter = QPainter(self)
                pen = QPen(QColor(0, 255, 0), 7)
                painter.setPen(pen)
                painter.drawLine(line_x, 0, line_x, self.height())

    def enable_line(self, enable=True, mode=None):
        self.mode = mode
        self.draw_line = enable
        self.update()  # Trigger Repaint
