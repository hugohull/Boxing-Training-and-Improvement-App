from PyQt5.QtChart import QChartView, QPieSeries, QChart
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QFormLayout, QGraphicsDropShadowEffect, QMainWindow, QStackedWidget, QAction, qApp, QMessageBox, QScrollArea, \
    QComboBox
from PyQt5.QtCore import pyqtSlot, Qt, QTimer, QUrl
from PyQt5.QtGui import QPixmap, QImage, QIntValidator, QColor, QDesktopServices, QBrush
import pyqtgraph as pg
from ImageLabel import ImageLabel
from styles import *
from utils import play_ding, show_error_message, show_history_reset_message, show_session_complete_message, \
    get_rand_url, get_quote
from VideoThread import VideoThread
from HistoryManager import *


def openRandomVideo():
    url = get_rand_url()
    QDesktopServices.openUrl(QUrl(url))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.show_label = False
        self.rest_seconds = None
        self.work_seconds = None
        self.openButton = None
        self.skill_level_label = None
        self.example_image_label = None
        self.track_punches = None
        self.skill_level_combo = None
        self.timerPage = None
        self.historyPage = None
        self.graph_specific_punch_widget = None
        self.homePage = None
        self.graph_competition_widget = None
        self.graph_specific_punch_chart = None
        self.reset_history_button = None
        self.quoteLabel = None
        self.stackedWidget = None
        self.graph_combination_widget = None
        self.graph_widget = None
        self.red_score_label = None
        self.blue_score_label = None
        self.blue_score = 0
        self.red_score = 0
        self.start_competition_mode_button = None
        self.is_competition_mode_active = None
        self.combination_label = None
        self.again = False
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
        self.correct_combination_label = QLabel()
        self.incorrect_combination_label = QLabel()
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
        if color == 'red':
            color_hex = 'rgba(255, 0, 0, 200)'
        elif color == 'blue':
            color_hex = 'rgba(0, 0, 255, 200)'
        elif color == 'green':
            color_hex = 'rgba(0, 255, 0, 200)'

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

        self.historyPage.setObjectName("HistoryPage")

        self.historyPage.setStyleSheet("""
            #HistoryPage {
                border-left: 15px solid rgba(180, 0, 0, 255);  /* Red stripe on the left */
                border-right: 15px solid rgba(15, 82, 152, 255);  /* Blue stripe on the right */
            }
        """)

        layout = QVBoxLayout()
        self.update_history_labels()
        layout.setContentsMargins(50, 10, 50, 30)  

        # Setting up the graph widget
        self.graph_widget = pg.PlotWidget()
        self.graph_widget.setBackground(None)
        self.graph_widget.setMinimumHeight(200)
        self.graph_widget.setTitle("Distribution of Total Punches.")
        self.graph_widget.setAlignment(Qt.AlignCenter)

        # Setting up the graph widget for correct vs incorrect
        self.graph_combination_widget = pg.PlotWidget()
        self.graph_combination_widget.setBackground(None)
        self.graph_combination_widget.setMinimumHeight(200)  # Set background to transparent
        self.graph_combination_widget.setTitle("Number of Correct vs. Incorrect Combinations Thrown.")
        self.graph_combination_widget.setAlignment(Qt.AlignCenter)

        # Setting up the graph widget for correct vs incorrect
        self.graph_specific_punch_chart = QChart()
        self.graph_specific_punch_widget = QChartView(self.graph_specific_punch_chart)
        self.graph_specific_punch_widget.setMinimumHeight(300)
        self.graph_specific_punch_widget.setAlignment(Qt.AlignCenter)

        # Setting up the graph widget for games statistics
        self.graph_competition_widget = pg.PlotWidget()
        self.graph_competition_widget.setBackground(None)
        self.graph_competition_widget.setMinimumHeight(200)
        self.graph_competition_widget.setTitle("Games Won vs Lost vs Drawn")
        self.graph_competition_widget.setAlignment(Qt.AlignCenter)

        # Handle wheel events by forwarding them to the scroll area
        for widget in [self.graph_widget, self.graph_combination_widget, self.graph_specific_punch_widget,
                       self.graph_competition_widget]:
            widget.wheelEvent = lambda event, w=widget: scroll_area.wheelEvent(event)

        # Create page title
        title = QLabel('History', self)
        title.setStyleSheet("font-size: 30px; font-weight: bold")
        title.setAlignment(Qt.AlignCenter)

        # Statistics subtitle
        statistics_subtitle = QLabel('Statistics:', self)
        statistics_subtitle.setStyleSheet("font-size: 20px; font-weight: bold")
        statistics_subtitle.setAlignment(Qt.AlignLeft)

        # Subtitle
        graphs_subtitle = QLabel('Graphs:', self)
        graphs_subtitle.setStyleSheet("font-size: 20px; font-weight: bold")
        graphs_subtitle.setAlignment(Qt.AlignLeft)

        layout.addWidget(title)  # Add the welcome label to the layout
        layout.addWidget(graphs_subtitle)

        # Scroll Area
        scroll_area = QScrollArea(self.historyPage)
        scroll_area_widget = QWidget()
        scroll_area_layout = QVBoxLayout(scroll_area_widget)

        # Add the graph widgets to the scroll area layout
        scroll_area_layout.addWidget(self.graph_specific_punch_widget)
        scroll_area_layout.addWidget(self.graph_widget)
        scroll_area_layout.addWidget(self.graph_combination_widget)
        scroll_area_layout.addWidget(self.graph_competition_widget)
        scroll_area_widget.setLayout(scroll_area_layout)
        scroll_area.setWidget(scroll_area_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumHeight(400)

        layout.addWidget(scroll_area)

        # Adding other widgets to layout.
        layout.addWidget(statistics_subtitle)
        layout.addWidget(self.total_punches_label)
        layout.addWidget(self.completed_rounds_label)
        layout.setAlignment(Qt.AlignTop)

        # Create Reset History button
        self.reset_history_button = QPushButton('Reset History', self)
        self.reset_history_button.clicked.connect(self.reset_history)  # Connect to the resetHistory method
        self.reset_history_button.setStyleSheet(red_button_style)

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(self.reset_history_button)
        button_layout.addStretch(1)
        layout.addLayout(button_layout)

        self.historyPage.setLayout(layout)

    def updateHistoryPage(self):
        self.update_history_labels()
        self.update_all_punch_bar_graph()
        self.update_combination_bar_graph()
        self.update_specific_punch_pie_chart()
        self.update_games_bar_graph()

    def setupHomePage(self):
        # Set up the home page layout and widgets
        self.homePage = QWidget()
        layout = QVBoxLayout(self.homePage)
        layout.setContentsMargins(10, 10, 10, 30)

        # Set stripes on each side of the widget that holds the layout
        self.homePage.setStyleSheet("""
            QWidget {
                border-left: 15px solid rgba(180, 0, 0, 255);  /* Red stripe on the left */
                border-right: 15px solid rgba(15, 82, 152, 255);  /* Blue stripe on the right */
            }
        """)

        # Group the title and subtitle in a vertical layout
        title_layout = QVBoxLayout()  
        title_layout.setSpacing(10)

        # Create welcome label
        welcome_label = QLabel('Welcome to BoxingApp', self.homePage)
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("QLabel { font-size: 30pt; font-weight: bold; }")
        title_layout.addWidget(welcome_label)

        # Subtitle
        subtitle_label = QLabel('The home of modern boxing training and improvement', self.homePage)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("QLabel { font-size: 20pt; font-weight: bold; }")
        title_layout.addWidget(subtitle_label)

        # Add title layout to the main layout
        layout.addLayout(title_layout)

        # Create image label
        self.image_label = QLabel(self.homePage)
        pixmap = QPixmap('Images/logo.png')
        pixmap = pixmap.scaled(450, 500, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.image_label)

        self.openButton = QPushButton("Click for motivation", self)
        self.openButton.clicked.connect(openRandomVideo)
        self.openButton.setStyleSheet(red_button_style)

        # Center the button using a horizontal layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.openButton)
        button_layout.addStretch()

        # Create quote label
        self.quoteLabel = QLabel("Quote will be here", self.homePage)
        self.quoteLabel.setAlignment(Qt.AlignCenter)
        self.quoteLabel.setObjectName("quoteLabel")
        self.quoteLabel.setWordWrap(True)
        self.quoteLabel.setStyleSheet("QLabel { font-size: 20pt; "
                                      "font-style: italic; "
                                      "}")

        # Add the quote label to the main layout
        layout.addWidget(self.quoteLabel)

        # Add the horizontal layout to the main layout
        layout.addLayout(button_layout)

        self.updateQuote()

        self.homePage.setLayout(layout)

    def updateQuote(self):
        quote = get_quote()
        self.quoteLabel.setText(quote)

    def setupTimerPage(self):

        self.timerPage.setObjectName("TimerPage")

        self.timerPage.setStyleSheet("""
            #TimerPage {
                border-left: 15px solid rgba(180, 0, 0, 255);  /* Red stripe on the left */
                border-right: 15px solid rgba(15, 82, 152, 255);  /* Blue stripe on the right */
            }
        """)

        # Layouts
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        form_layout = QFormLayout()

        # Labels
        self.image_label = ImageLabel(self)
        self.image_label.enable_line(False)
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

        # Create image label
        self.example_image_label = QLabel(self.homePage)
        pixmap = QPixmap('Images/Example.png')
        pixmap = pixmap.scaled(350, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.example_image_label.setPixmap(pixmap)
        self.example_image_label.setAlignment(Qt.AlignCenter)
        shadow_effect_example = QGraphicsDropShadowEffect(self.image_label)
        shadow_effect_example.setBlurRadius(10)  # Shadow size
        shadow_effect_example.setColor(QColor(0, 0, 0, 60))  # Shadow color and transparency
        shadow_effect_example.setOffset(5, 5)  # Shadow offset
        self.example_image_label.setGraphicsEffect(shadow_effect_example)

        # Combination Label
        self.combination_label = QLabel('Combination', self)
        self.combination_label.setAlignment(Qt.AlignCenter)
        self.combination_label.setStyleSheet("font-size: 28px; font-weight: bold;")
        self.combination_label.hide()

        # Score labels
        self.red_score_label = QLabel('Red Score: 0', self)
        self.red_score_label.setStyleSheet("color: red; font-size: 24px; font-weight: bold")
        self.red_score_label.hide()

        self.blue_score_label = QLabel('Blue Score: 0', self)
        self.blue_score_label.setStyleSheet("color: dodgerblue; font-size: 24px; font-weight: bold;")
        self.blue_score_label.hide()

        # Score Layout
        score_layout = QHBoxLayout()
        score_layout.setContentsMargins(40, 0, 40, 0) 

        # Add labels to the layout with alignment
        score_layout.addWidget(self.red_score_label, 0, Qt.AlignLeft)
        score_layout.addWidget(self.blue_score_label, 0, Qt.AlignRight)

        # Inputs
        self.round_input = QLineEdit(self)
        self.work_input = QLineEdit(self)
        self.rest_input = QLineEdit(self)

        self.skill_level_combo = QComboBox(self)
        self.skill_level_combo.addItems(["Beginner", "Intermediate", "Advanced"])

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
        self.start_competition_mode_button = QPushButton('Start Competition Mode', self)
        self.start_competition_mode_button.setStyleSheet(green_button_style)
        self.start_competition_mode_button.clicked.connect(self.start_competition_mode)
        self.pause_button = QPushButton('Pause Timer', self)
        self.pause_button.setStyleSheet(blue_button_style)
        self.pause_button.clicked.connect(self.toggle_pause)
        self.pause_button.hide()

        self.thread = None

        # Setting placeholders
        self.round_input.setPlaceholderText("Enter number of rounds.")
        self.work_input.setPlaceholderText("Enter number of seconds (Work).")
        self.rest_input.setPlaceholderText("Enter number of seconds (Rest).")
        # self.round_input.setText("3")
        # self.work_input.setText("30")
        # self.rest_input.setText("30")

        # Container for buttons
        button_container = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.start_button)
        buttons_layout.addWidget(self.start_with_video_button)
        buttons_layout.addWidget(self.start_training_mode_button)
        buttons_layout.addWidget(self.start_competition_mode_button)
        buttons_layout.addWidget(self.pause_button)
        buttons_layout.setAlignment(Qt.AlignCenter)
        button_container.setLayout(buttons_layout)

        label_wrapper = QWidget()
        label_wrapper_layout = QVBoxLayout()
        label_wrapper_layout.addWidget(self.timer_label)
        label_wrapper_layout.setAlignment(self.timer_label, Qt.AlignCenter)
        label_wrapper.setLayout(label_wrapper_layout)

        # Add the timer label & round label
        main_layout.addWidget(label_wrapper)
        main_layout.addWidget(self.round_label)
        main_layout.addWidget(self.phase_label)
        main_layout.addWidget(self.example_image_label)

        # Form layout for inputs
        self.round_input_label = QLabel('Rounds:')
        form_layout.addRow(self.round_input_label, self.round_input)

        self.work_time_label = QLabel('Work Time (sec):')
        form_layout.addRow(self.work_time_label, self.work_input)

        self.rest_time_label = QLabel('Rest Time (sec):')
        form_layout.addRow(self.rest_time_label, self.rest_input)

        self.skill_level_label = QLabel('Skill Level:')
        form_layout.addRow(self.skill_level_label, self.skill_level_combo)

        # Adding widgets to main layout
        main_layout.addLayout(form_layout)
        main_layout.addWidget(button_container)
        main_layout.addLayout(score_layout)
        main_layout.addWidget(self.image_label)
        main_layout.addWidget(self.combination_label)

        # Set the layout to the timer page
        self.timerPage.setLayout(main_layout)

    def setHistoryPage(self):
        self.updateHistoryPage()
        self.stackedWidget.setCurrentWidget(self.historyPage)

    def setTimerPage(self):
        self.stackedWidget.setCurrentWidget(self.timerPage)

    def setHomePage(self):
        self.stackedWidget.setCurrentWidget(self.homePage)
        self.updateQuote()

    # Timer functions
    def start_timer(self):
        self.again = False
        # Initial input validation
        if not self.round_input.text().isdigit():
            self.image_label.hide()
            show_error_message("Round field cannot be empty.")
        elif not self.work_input.text().isdigit():
            self.image_label.hide()
            show_error_message("Work field cannot be empty.")
        elif not self.rest_input.text().isdigit():
            self.image_label.hide()
            show_error_message("Rest field cannot be empty.")
        else:
            # Input conversion
            self.rounds = int(self.round_input.text())
            self.work_seconds = int(self.work_input.text())
            self.rest_seconds = int(self.rest_input.text())

            if self.rounds == 0:
                self.image_label.hide()
                show_error_message("Number of rounds cannot be zero.")
                self.image_label.hide()
            elif self.work_seconds == 0:
                self.image_label.hide()
                show_error_message("Work seconds cannot be zero.")
            elif self.rest_seconds == 0:
                self.image_label.hide()
                show_error_message("Rest seconds cannot be zero.")
            else:
                self.show_label = True
                self.default_round = int(self.round_input.text())
                self.start_work()
                self.pause_button.show()
                self.start_button.setText('Stop Timer')
                self.start_button.setStyleSheet(red_button_style)
                self.start_button.clicked.disconnect()
                self.start_button.clicked.connect(self.stop_timer)
                self.start_with_video_button.hide()
                self.start_training_mode_button.hide()
                self.start_competition_mode_button.hide()
                self.update_round_label()

    def start_work(self):
        if self.last_used_mode == "Tracking":
            self.toggle_modes(tracker_mode=True, training_mode=False, competition_mode=False)
        elif self.last_used_mode == "Training":
            self.toggle_modes(tracker_mode=False, training_mode=True, competition_mode=False)
        elif self.last_used_mode == "Competition":
            self.toggle_modes(tracker_mode=False, training_mode=False, competition_mode=True)
        if self.thread is not None:
            self.thread.skill_level = self.skill_level_combo.currentText()
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
        self.skill_level_label.hide()
        self.skill_level_combo.hide()
        self.example_image_label.hide()

    def start_rest(self):
        self.toggle_modes(tracker_mode=False, training_mode=False, competition_mode=False)
        self.current_phase = 'rest'
        self.phase_label.setText('Rest')
        self.current_phase = 'rest'
        self.seconds_left = int(self.rest_input.text())
        play_ding()
        self.timer.start(1000)
        self.update_round_label()

    def next_round(self):
        self.rounds -= 1
        punch_history = get_punch_history()
        punch_history['Completed Rounds'] += 1
        save_punch_history(punch_history)
        if self.rounds > 0:
            self.current_round += 1

            self.start_work()
        else:
            play_ding()
            self.timer_label.setText("Done!")
            self.update_round_label()
            self.again = True
            history = get_punch_history()

            if self.red_score > self.blue_score:
                history["Games Won"] += 1
                save_punch_history(history)
            elif self.red_score < self.blue_score:
                history["Games Lost"] += 1
                save_punch_history(history)
            elif self.red_score == self.blue_score:
                history["Games Drawn"] += 1
                save_punch_history(history)

            self.toggle_modes(tracker_mode=False, training_mode=False, competition_mode=False)
            show_session_complete_message()
            self.timer_label.setText("00:00")
            self.image_label.hide()
            self.combination_label.hide()
            self.red_score_label.hide()
            self.blue_score_label.hide()
            self.reset_timer()

    def reset_timer(self):
        self.show_label = False
        self.rounds = 0
        self.current_round = 1
        self.last_used_mode = None
        self.toggle_modes(tracker_mode=False, training_mode=False, competition_mode=False)
        self.start_button.setText('Start Timer')  # Change the button text to 'Start Timer'
        self.start_button.setStyleSheet(green_button_style)
        self.pause_button.hide()
        self.timer_label.setText('00:00')
        self.round_label.setText('Round 01/12')
        self.red_score = 0
        self.red_score_label.setText("Red score: 0")
        self.blue_score = 0
        self.blue_score_label.setText("Blue score: 0")
        self.start_button.clicked.disconnect()
        self.start_button.clicked.connect(self.start_timer)
        self.start_with_video_button.show()
        self.start_training_mode_button.show()
        self.start_competition_mode_button.show()
        self.phase_label.hide()
        # Show inputs and labels
        self.round_input_label.show()
        self.round_input.show()
        self.work_time_label.show()
        self.work_input.show()
        self.rest_time_label.show()
        self.rest_input.show()
        self.skill_level_label.show()
        self.skill_level_combo.show()
        self.example_image_label.show()

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
            self.toggle_modes(tracker_mode=False, training_mode=False, competition_mode=False)
            self.timer.stop()
            self.pause_button.setText('Resume Timer')
            self.pause_button.setStyleSheet(green_button_style)
        else:
            if self.last_used_mode == "Tracking":
                self.toggle_modes(tracker_mode=True, training_mode=False, competition_mode=False)
            elif self.last_used_mode == "Training":
                self.toggle_modes(tracker_mode=False, training_mode=True, competition_mode=False)
            self.timer.start(1000)
            self.pause_button.setText('Pause Timer')
            self.pause_button.setStyleSheet(blue_button_style)

    def update_round_label(self):
        # Update the text of round_label to reflect the current state
        self.round_label.setText(f'Round {self.current_round:02}/{self.default_round}')

    def stop_timer(self):
        self.image_label.enable_line(enable=False)
        self.toggle_modes(tracker_mode=False, training_mode=False, competition_mode=False)
        if self.thread is not None:
            # self.thread.stop()
            self.image_label.hide()
            self.combination_label.hide()
            self.red_score_label.hide()
            self.blue_score_label.hide()
            self.thread = None
        self.timer.stop()  # Stop the timer
        self.phase_label.setText('Done!')
        self.reset_timer()

    @pyqtSlot(QImage)
    def set_image(self, image):
        if self.thread is not None:
            self.image_label.setPixmap(QPixmap.fromImage(image))

    def toggle_modes(self, tracker_mode, training_mode, competition_mode):
        if self.thread:
            self.thread.tracker_mode_active = tracker_mode
            self.thread.training_mode_active = training_mode
            self.thread.competition_mode_active = competition_mode
        self.is_tracker_mode_active = tracker_mode
        self.is_training_mode_active = training_mode
        self.is_competition_mode_active = competition_mode

    def start_timer_and_video(self):
        self.image_label.enable_line(True, mode="Tracking")
        self.last_used_mode = "Tracking"
        if self.thread is None or not self.thread.isRunning() or self.again:
            if self.again:
                self.again = False
            self.thread = VideoThread()
            self.toggle_modes(tracker_mode=True, training_mode=False, competition_mode=False)
            self.thread.change_pixmap_signal.connect(self.set_image)
            self.thread.flash_needed.connect(self.flash_color)
            self.thread.start()
        self.start_timer()
        self.phase_label.show()
        if self.show_label == True:
            self.image_label.show()
            self.image_label.setAlignment(Qt.AlignCenter)

    def start_training_mode(self):
        self.image_label.enable_line(True, mode="Training")
        self.last_used_mode = "Training"
        # Ensure only one instance of VideoThread is running
        if self.thread is None or not self.thread.isRunning() or self.again:
            if self.again:
                self.again = False
            self.is_training_mode_active = True
            self.thread = VideoThread(mode='training')
            self.thread.new_combination_signal.connect(self.update_combination_display)
            self.toggle_modes(tracker_mode=False, training_mode=True, competition_mode=False)
            self.thread.change_pixmap_signal.connect(self.set_image)
            self.thread.flash_needed.connect(self.flash_color)
            self.thread.start()
        self.start_timer()
        self.phase_label.show()
        if self.show_label == True:
            self.image_label.show()
            self.combination_label.show()
            self.image_label.setAlignment(Qt.AlignCenter)

    def update_red_score(self):
        self.red_score += 1
        self.red_score_label.setText(f'Red Score: {self.red_score}')

    def update_blue_score(self):
        self.blue_score += 1
        self.blue_score_label.setText(f'Blue Score: {self.blue_score}')

    def start_competition_mode(self):
        self.image_label.enable_line(True, mode="Competition")
        self.last_used_mode = "Competition"
        if self.thread is None or not self.thread.isRunning() or self.again:
            if self.again:
                self.again = False
            self.is_competition_mode_active = True
            self.thread = VideoThread(mode='competition')
            self.thread.new_combination_signal.connect(self.update_combination_display)
            self.thread.update_red_score_signal.connect(self.update_red_score)
            self.thread.update_blue_score_signal.connect(self.update_blue_score)
            self.toggle_modes(tracker_mode=False, training_mode=False, competition_mode=True)
            self.thread.change_pixmap_signal.connect(self.set_image)
            self.thread.flash_needed.connect(self.flash_color)
            self.thread.start()
        self.start_timer()
        self.phase_label.show()
        if self.show_label == True:
            self.image_label.show()
            self.combination_label.show()
            self.red_score_label.show()
            self.blue_score_label.show()
            self.image_label.setAlignment(Qt.AlignCenter)

    def update_combination_display(self, combination):
        # Update the GUI with the new combination
        self.combination_label.setText(f"Combination: {combination}")

    def update_history_labels(self):
        punch_history = get_punch_history()
        self.total_punches_label.setText(f'Total Punches: {punch_history["Total Punches"]}')
        self.completed_rounds_label.setText(f'Completed Rounds: {punch_history["Completed Rounds"]}')

    def reset_history(self):
        reply = QMessageBox.question(self, 'Confirm Reset',
                                     "Are you sure you want to erase your history?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            reset_punch_history()
            self.update_history_labels()
            self.update_combination_bar_graph()
            self.update_specific_punch_pie_chart()
            self.update_all_punch_bar_graph()
            self.update_games_bar_graph()
            self.update_history_labels()
            show_history_reset_message()

    def update_all_punch_bar_graph(self):
        punch_history = get_punch_history()
        categories = ['Total Left Punches', 'Total Right Punches', 'Total Head Punches', 'Total Body Punches']
        y_values = [punch_history["Total Left"], punch_history["Total Right"], punch_history["Total Head"],
                    punch_history["Total Body"]]

        # Define colors for each category
        brushes = [(180, 0, 0, 255), (15, 82, 152, 255), (128, 0, 128, 255), (128, 0, 128, 255)]  # RGBA values

        # Clear the previous graph
        self.graph_widget.clear()

        # Create the bar graph
        for i, (category, y, brush) in enumerate(zip(categories, y_values, brushes)):
            bar_graph = pg.BarGraphItem(x=[i], height=[y], width=0.5, brush=brush)
            self.graph_widget.addItem(bar_graph)

        # Update x-axis to show category names instead of numbers
        axis = self.graph_widget.getAxis('bottom')
        axis.setTicks([list(zip(range(len(categories)), categories))])

        # Adding text labels on top of each bar
        for x, y, label in zip(range(len(categories)), y_values, y_values):
            text = pg.TextItem(f'{label}', color=(200, 200, 200), anchor=(0.5, 0))
            self.graph_widget.addItem(text)
            text.setPos(x, y)

    def update_combination_bar_graph(self):
        punch_history = get_punch_history()
        correct = punch_history.get("Correct Combinations", 0)
        incorrect = punch_history.get("Incorrect Combinations", 0)

        categories = ['Correct Combinations', 'Incorrect Combinations']
        values = [correct, incorrect]
        colors = [QColor('green'), (180, 0, 0, 255)]

        self.graph_combination_widget.clear()
        for i, val in enumerate(values):
            bar_graph = pg.BarGraphItem(x=[i], height=[val], width=0.6, brush=colors[i])
            self.graph_combination_widget.addItem(bar_graph)
            # Create a text item for each bar
            text = pg.TextItem(f'{val}', color=(200, 200, 200), anchor=(0.5, 0))  # Black color for visibility
            self.graph_combination_widget.addItem(text)
            text.setPos(i, val)  # Position text at the top of each bar

        # Update x-axis to show category names
        axis = self.graph_combination_widget.getAxis('bottom')
        axis.setTicks([list(zip(range(len(categories)), categories))])

    def update_specific_punch_pie_chart(self):
        punch_history = get_punch_history()
        categories = ['Left Head Punches', 'Left Body Punches', 'Right Head Punches', 'Right Body Punches']
        values = [punch_history.get("Left Head", 0), punch_history.get("Left Body", 0),
                  punch_history.get("Right Head", 0), punch_history.get("Right Body", 0)]

        # Clear the previous chart
        self.graph_specific_punch_chart.removeAllSeries()

        # Colors corresponding to each punch type
        colors = [QColor(180, 0, 0, 255), QColor(128, 0, 128, 255), QColor(15, 82, 152, 255), QColor(0, 150, 0, 255)]

        # Create pie series
        series = QPieSeries()
        series.setPieSize(1)
        for category, value, color in zip(categories, values, colors):
            pie_slice = series.append(category + f" ({value})", value)
            pie_slice.setBrush(color)

        # Add the series to the chart
        self.graph_specific_punch_chart.addSeries(series)
        self.graph_specific_punch_chart.setTitleBrush(QBrush(QColor(150, 150, 150)))
        self.graph_specific_punch_chart.setTitle("Distribution of Specific Punches.")

        self.graph_specific_punch_chart.setBackgroundBrush(QBrush(QColor(0, 0, 0, 0)))

        self.graph_specific_punch_chart.legend().setVisible(True)
        self.graph_specific_punch_chart.legend().setLabelColor(QColor(150, 150, 150))
        self.graph_specific_punch_chart.legend().setAlignment(Qt.AlignBottom)

    def update_games_bar_graph(self):
        punch_history = get_punch_history()
        categories = ['Games Won', 'Games Lost', 'Games Drawn']
        y_values = [punch_history.get("Games Won", 0), punch_history.get("Games Lost", 0),
                    punch_history.get("Games Drawn", 0)]

        brushes = [(180, 0, 0, 255), (15, 82, 152, 255), (128, 0, 128, 255)]  # Red, Blue, Purple

        self.graph_competition_widget.clear()

        for i, (category, y, brush) in enumerate(zip(categories, y_values, brushes)):
            bar_graph = pg.BarGraphItem(x=[i], height=[y], width=0.5, brush=brush)
            self.graph_competition_widget.addItem(bar_graph)

            # Adding text labels on top of each bar
            text = pg.TextItem(f'{y}', color=(200, 200, 200), anchor=(0.5, 0))
            self.graph_competition_widget.addItem(text)
            text.setPos(i, y)

        axis = self.graph_competition_widget.getAxis('bottom')
        axis.setTicks([list(zip(range(len(categories)), categories))])
