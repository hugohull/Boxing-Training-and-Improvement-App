from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QFormLayout, QGraphicsDropShadowEffect, QMainWindow, QStackedWidget, QAction, qApp
from PyQt5.QtCore import pyqtSlot, Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QIntValidator, QColor, QFont

from punch_tracker import run_training_mode
from styles import *
from utils import play_ding, show_error_message, show_history_updated_message, show_session_complete_message
from VideoThread import VideoThread
from HistoryManager import *


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.last_used_mode = None
        self.start_training_mode_button = None
        self.is_training_mode_active = False
        self.is_tracker_mode_active = False
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
        self.total_punches_label = QLabel()
        self.total_left_label = QLabel()
        self.total_right_label = QLabel()
        self.total_head_label = QLabel()
        self.total_body_label = QLabel()
        self.left_head_label = QLabel()
        self.left_body_label = QLabel()
        self.right_head_label = QLabel()
        self.right_body_label = QLabel()
        self.completed_rounds_label = QLabel()
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
        self.flash_timer = QTimer(self)
        self.flash_timer.timeout.connect(self.end_flash)
        self.initUI()

    def flash_color(self, color):
        # Set the background color to red or blue depending on the detected object
        color_hex = 'rgba(255, 0, 0, 200)' if color == 'red' else 'rgba(0, 0, 255, 200)'
        self.image_label.setStyleSheet(f"border: 5px solid {color_hex};")
        self.flash_timer.start(200)  # Start the timer for the flash duration

    def end_flash(self):
        self.image_label.setStyleSheet("border: 5px solid transparent;")
        self.flash_timer.stop()  # Stop the timer

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create the stacked widget
        self.stackedWidget = QStackedWidget()
        self.setCentralWidget(self.stackedWidget)

        # Create individual pages
        self.homePage = QWidget()
        self.historyPage = QWidget()
        self.timerPage = QWidget()

        # Setup each page
        self.setupHistoryPage()
        self.setupHomePage()
        self.setupTimerPage()

        # Add pages to the stacked widget
        self.stackedWidget.addWidget(self.homePage)
        self.stackedWidget.addWidget(self.historyPage)
        self.stackedWidget.addWidget(self.timerPage)

        # Actions
        homeAct = QAction('Home', self)
        homeAct.setStatusTip('Return to Home')
        homeAct.triggered.connect(self.setHomePage)

        timerAct = QAction('Timer', self)
        timerAct.setStatusTip('Open timer')
        timerAct.triggered.connect(self.setTimerPage)

        historyAct = QAction('History', self)
        historyAct.setStatusTip('View history')
        historyAct.triggered.connect(self.setHistoryPage)

        exitAct = QAction('Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        # Menu bar
        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(homeAct)
        fileMenu.addAction(timerAct)
        fileMenu.addAction(historyAct)
        fileMenu.addAction(exitAct)

        # Toolbar
        toolbar = self.addToolBar('MainToolbar')
        toolbar.addAction(homeAct)
        toolbar.addAction(timerAct)
        toolbar.addAction(historyAct)
        toolbar.addAction(exitAct)

        self.show()

    def setupHistoryPage(self):
        layout = QVBoxLayout()
        self.update_history_labels()
        # Labels and buttons for the layout
        layout.addWidget(self.total_punches_label)
        layout.addWidget(self.total_left_label)
        layout.addWidget(self.total_right_label)
        layout.addWidget(self.total_head_label)
        layout.addWidget(self.total_body_label)
        layout.addWidget(self.left_head_label)
        layout.addWidget(self.left_body_label)
        layout.addWidget(self.right_head_label)
        layout.addWidget(self.right_body_label)
        layout.addWidget(self.completed_rounds_label)
        # layout.addWidget(history_button)
        layout.setAlignment(Qt.AlignTop)

        self.historyPage.setLayout(layout)

    def updateHistoryPage(self):
        self.update_history_labels()

    def setupHomePage(self):
        # Set up the home page layout and widgets
        layout = QVBoxLayout()

        # Create welcome label
        welcome_label = QLabel('Welcome to BoxingApp', self)
        welcome_label.setAlignment(Qt.AlignCenter)
        # Set font using QFont
        font = QFont()
        font.setPointSize(30)  # Set font size
        font.setBold(True)  # Set font weight to bold
        welcome_label.setFont(font)  # Apply the font to the welcome label
        layout.addWidget(welcome_label)  # Add the welcome label to the layout

        # Create image label
        self.image_label = QLabel(self)
        pixmap = QPixmap('Images/gloves.jpg')
        pixmap = pixmap.scaled(450, 500, Qt.KeepAspectRatio)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        self.homePage.setLayout(layout)

    def setupTimerPage(self):
        # Layouts
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)  # Sets the spacing between widgets in the layout to 10 pixels
        main_layout.setContentsMargins(10, 10, 10, 10)  # Sets the margins of the layout (left, top, right, bottom)

        form_layout = QFormLayout()
        buttons_layout = QHBoxLayout()

        # Labels
        self.image_label = QLabel(self)
        self.image_label.setStyleSheet("border: 5px solid transparent;")
        shadow_effect = QGraphicsDropShadowEffect(self.image_label)
        shadow_effect.setBlurRadius(10)  # Shadow size
        shadow_effect.setColor(QColor(0, 0, 0, 60))  # Shadow color and transparency
        shadow_effect.setOffset(5, 5)  # Shadow offset
        self.image_label.setGraphicsEffect(shadow_effect)

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
        self.start_training_mode_button = QPushButton('Start Training Mode', self)
        self.start_training_mode_button.setStyleSheet(green_button_style)
        self.start_training_mode_button.clicked.connect(self.start_training_mode)
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
        buttons_layout.addWidget(self.start_training_mode_button)
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

        # Set the layout to the timer page
        self.timerPage.setLayout(main_layout)

    def setHistoryPage(self):
        self.updateHistoryPage()
        self.stackedWidget.setCurrentWidget(self.historyPage)

    def setTimerPage(self):
        self.stackedWidget.setCurrentWidget(self.timerPage)

    def setHomePage(self):
        self.stackedWidget.setCurrentWidget(self.homePage)

    # Timer functions
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
            self.start_training_mode_button.hide()
            self.update_round_label()

    def start_work(self):
        if self.last_used_mode == "Tracking":
            self.toggle_modes(tracker_mode=True, training_mode=False)
        elif self.last_used_mode == "Training":
            self.toggle_modes(tracker_mode=False, training_mode=True)
        self.current_phase = 'work'
        self.phase_label.show()
        self.phase_label.setText('Work')  # Update the phase label text
        self.current_phase = 'work'
        self.seconds_left = int(self.work_input.text())
        play_ding()
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
        self.toggle_modes(tracker_mode=False, training_mode=False)
        self.current_phase = 'rest'
        self.phase_label.setText('Rest')
        self.current_phase = 'rest'
        self.seconds_left = int(self.rest_input.text())
        play_ding()
        self.timer.start(1000)
        self.update_round_label()

    def next_round(self):
        self.rounds -= 1
        punch_history = load_punch_history()
        punch_history['Completed Rounds'] += 1
        save_punch_history(punch_history)
        if self.rounds > 0:
            self.current_round += 1

            self.start_work()
        else:
            play_ding()
            self.timer_label.setText("Done!")
            self.update_round_label()
            show_session_complete_message()
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
        self.start_training_mode_button.show()
        # self.image_label.hide()
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
            self.track_punches = False
            self.toggle_modes(tracker_mode=False, training_mode=False)
            self.timer.stop()
            self.pause_button.setText('Resume Timer')
            self.pause_button.setStyleSheet(green_button_style)  # Optional: Change style if you want to indicate resume
        else:
            if self.last_used_mode == "Tracking":
                self.toggle_modes(tracker_mode=True, training_mode=False)
            elif self.last_used_mode == "Training":
                self.toggle_modes(tracker_mode=False, training_mode=True)
            self.timer.start(1000)
            self.pause_button.setText('Pause Timer')
            self.pause_button.setStyleSheet(blue_button_style)

    def update_round_label(self):
        # Update the text of round_label to reflect the current state
        self.round_label.setText(f'Round {self.current_round:02}/{self.default_round}')

    def stop_timer(self):
        self.toggle_modes(tracker_mode=False, training_mode=False)
        if self.thread is not None:
            # self.thread.stop()
            self.image_label.hide()
            self.thread = None
        self.timer.stop()  # Stop the timer
        self.phase_label.setText('Done!')
        self.reset_timer()

    @pyqtSlot(QImage)
    def set_image(self, image):
        if self.thread is not None:
            self.image_label.setPixmap(QPixmap.fromImage(image))

    def toggle_modes(self, tracker_mode, training_mode):
        if self.thread:
            self.thread.tracker_mode_active = tracker_mode
            self.thread.training_mode_active = training_mode
        self.is_tracker_mode_active = tracker_mode
        self.is_training_mode_active = training_mode

    def start_timer_and_video(self):
        self.last_used_mode = "Tracking"
        self.start_timer()
        self.phase_label.show()
        if self.thread is None or not self.thread.isRunning():
            self.thread = VideoThread()  # No need to pass flash_screen_callback
            self.toggle_modes(tracker_mode=True, training_mode=False)
            self.thread.change_pixmap_signal.connect(self.set_image)
            self.thread.flash_needed.connect(self.flash_color)  # Connect the new signal
            self.thread.start()
        self.image_label.show()
        self.image_label.setAlignment(Qt.AlignCenter)

    def start_training_mode(self):
        self.last_used_mode = "Training"
        self.start_timer()
        self.phase_label.show()
        # Ensure only one instance of VideoThread is running
        if self.thread is None or not self.thread.isRunning():
            self.is_training_mode_active = True
            self.thread = VideoThread(mode='training')
            self.toggle_modes(tracker_mode=False, training_mode=True)
            self.thread.change_pixmap_signal.connect(self.set_image)
            self.thread.flash_needed.connect(self.flash_color)
            self.thread.start()
        self.image_label.show()
        self.image_label.setAlignment(Qt.AlignCenter)

    def update_history_labels(self):
        punch_history = load_punch_history()
        self.total_punches_label.setText(f'Total Punches: {punch_history["Total Punches"]}')
        self.total_left_label.setText(f'Total Left: {punch_history["Total Left"]}')
        self.total_right_label.setText(f'Total Right: {punch_history["Total Right"]}')
        self.total_head_label.setText(f'Total Head: {punch_history["Total Head"]}')
        self.total_body_label.setText(f'Total Body: {punch_history["Total Body"]}')
        self.left_head_label.setText(f'Left Head: {punch_history["Left Head"]}')
        self.left_body_label.setText(f'Left Body: {punch_history["Left Body"]}')
        self.right_head_label.setText(f'Right Head: {punch_history["Right Head"]}')
        self.right_body_label.setText(f'Right Body: {punch_history["Right Body"]}')
        self.completed_rounds_label.setText(f'Completed Rounds: {punch_history["Completed Rounds"]}')
