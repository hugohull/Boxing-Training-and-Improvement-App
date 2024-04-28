import threading

from PyQt5.QtWidgets import QMessageBox
from pydub import AudioSegment
from pydub.playback import play

ding = AudioSegment.from_mp3("Audio/Boxing Bell Sound.mp3")
correct = AudioSegment.from_mp3("Audio/Correct.mp3")
incorrect = AudioSegment.from_mp3("Audio/Incorrect.mp3")


def play_ding():
    # Using a thread to avoid blocking the GUI while playing sound
    threading.Thread(target=lambda: play(ding), daemon=True).start()

def play_correct():
    # Using a thread to avoid blocking the GUI while playing sound
    threading.Thread(target=lambda: play(correct), daemon=True).start()

def play_incorrect():
    threading.Thread(target=lambda: play(incorrect), daemon=True).start()


def show_error_message(message):
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setText(f"Error: {message}")
    error_dialog.setWindowTitle("Error")
    error_dialog.setStandardButtons(QMessageBox.Ok)
    error_dialog.exec_()

def show_history_reset_message():
    message_dialog = QMessageBox()
    message_dialog.setIcon(QMessageBox.Information)
    message_dialog.setText("Punch history has been successfully reset.")
    message_dialog.setWindowTitle("History Updated")
    message_dialog.setStandardButtons(QMessageBox.Ok)
    message_dialog.exec_()

def show_session_complete_message():
    message_dialog = QMessageBox()
    message_dialog.setIcon(QMessageBox.Information)
    message_dialog.setText("Your session is done!")
    message_dialog.setWindowTitle("Session complete")
    message_dialog.setStandardButtons(QMessageBox.Ok)
    message_dialog.exec_()