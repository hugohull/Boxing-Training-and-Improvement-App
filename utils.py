import threading

from PyQt5.QtWidgets import QMessageBox
from pydub import AudioSegment
from pydub.playback import play

ding = AudioSegment.from_mp3("Audio/Boxing Bell Sound.mp3")


def play_sound():
    # Using a thread to avoid blocking the GUI while playing sound
    threading.Thread(target=lambda: play(ding), daemon=True).start()


def show_error_message(message):
    error_dialog = QMessageBox()
    error_dialog.setIcon(QMessageBox.Critical)
    error_dialog.setText(f"Error: {message}")
    error_dialog.setWindowTitle("Error")
    error_dialog.setStandardButtons(QMessageBox.Ok)
    error_dialog.exec_()

def show_history_updated_message():
    message_dialog = QMessageBox()
    message_dialog.setIcon(QMessageBox.Information)
    message_dialog.setText("Punch history has been successfully refreshed.")
    message_dialog.setWindowTitle("History Updated")
    message_dialog.setStandardButtons(QMessageBox.Ok)
    message_dialog.exec_()