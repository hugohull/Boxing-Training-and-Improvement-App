import random
import threading

from PyQt5.QtWidgets import QMessageBox
from pydub import AudioSegment
from pydub.playback import play

ding = AudioSegment.from_mp3("Audio/Boxing Bell Sound.mp3")
correct = AudioSegment.from_mp3("Audio/Correct.mp3")
incorrect = AudioSegment.from_mp3("Audio/Incorrect.mp3")

video_urls = ['https://www.youtube.com/watch?v=GUzbP-3Yeq8', 'https://www.youtube.com/watch?v=TkbxWCnIMW8',
              'https://www.youtube.com/watch?v=XSHMW6i0gcM', 'https://www.youtube.com/watch?v=-yoJFBzxRYU',
              'https://www.youtube.com/watch?v=wBkTtOrP0qY', 'https://www.youtube.com/watch?v=pcBH6miSHxA',
              'https://www.youtube.com/watch?v=br-9pBT2QEw', 'https://www.youtube.com/watch?v=OR9Gg_PrFow',
              'https://www.youtube.com/watch?v=mrWjVxyhJV4', 'https://www.youtube.com/watch?v=e4mBsL2MmZA',
              'https://www.youtube.com/watch?v=-xF97Neu29c', 'https://www.youtube.com/watch?v=UChhi9sk7Gk',
              'https://www.youtube.com/watch?v=MgjKNpJkiRo', 'https://www.youtube.com/watch?v=MV0KGxuFemc',
              'https://www.youtube.com/watch?v=NWianH0BKos', 'https://www.youtube.com/watch?v=8w7yyTG7Qpw',
              'https://www.youtube.com/watch?v=kNhjJOFGJj8', 'https://www.youtube.com/watch?v=EJ3mxGDG-fw',
              'https://www.youtube.com/watch?v=lRTa9htVYDk', 'https://www.youtube.com/watch?v=WDoh6S6RimI',
              'https://www.youtube.com/watch?v=pDlOA1B2OKc', 'https://www.youtube.com/watch?v=851TxLduWHo',
              'https://www.youtube.com/watch?v=orxPPQmmB7I', 'https://www.youtube.com/watch?v=MJzAGTzCsrQ',
              'https://www.youtube.com/watch?v=t6Buh2iWAS8', 'https://www.youtube.com/watch?v=G7RKBfLkn7A',
              'https://www.youtube.com/watch?v=JDklZiG05ao', 'https://www.youtube.com/watch?v=n_FatpBHjTQ',
              'https://www.youtube.com/watch?v=cdnlVLeGlwc', 'https://www.youtube.com/watch?v=EULjlsI2Ps4',
              'https://www.youtube.com/watch?v=CxsdES3_WRo', 'https://www.youtube.com/watch?v=Uj9PW1bsS9A',
              'https://www.youtube.com/watch?v=x1Uoa0ISA_I', 'https://www.youtube.com/watch?v=DqjqJCUf_B4',
              'https://www.youtube.com/watch?v=fZC6uYJW7dQ', 'https://www.youtube.com/watch?v=xdI5b10i3c0',
              'https://www.youtube.com/watch?v=10Bv5FXvs1Y', 'https://www.youtube.com/watch?v=uVxSgm2GGmY',
              'https://www.youtube.com/watch?v=WUwfW1LohOI', 'https://www.youtube.com/watch?v=uD1SsoxzYyA',
              'https://www.youtube.com/watch?v=sJEfYY8kL1E', 'https://www.youtube.com/watch?v=Pj4jMkjjpXE',
              'https://www.youtube.com/watch?v=BTCAMRbgCsk', 'https://www.youtube.com/watch?v=UPJRChlqACY',
              'https://www.youtube.com/watch?v=ZGN_MCvROrY', 'https://www.youtube.com/watch?v=zGrf3cH00eU',
              'https://www.youtube.com/watch?v=Bpu-KDmKGDY', 'https://www.youtube.com/watch?v=9kLVYLvNThU',
              'https://www.youtube.com/watch?v=tk9VhHQN2T0', 'https://www.youtube.com/watch?v=bUMsTQxffPw']


def get_rand_url():
    return random.choice(video_urls)


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
