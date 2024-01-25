import threading
from tkinter import *
import time
from _datetime import datetime, timedelta
from pydub import AudioSegment
from pydub.playback import play

FONT = ("Calibri", 14)

ding = AudioSegment.from_mp3("Audio/Boxing Bell Sound.mp3")


def start():
    rounds = int(round_input.get())

    while rounds > 0:
        sound_thread = threading.Thread(target=play_sound, args=(ding,))
        sound_thread.start()

        round_seconds = int(work_input.get())

        # Work round
        while round_seconds > 0:
            # # Timer represents time left on countdown
            # timer = timedelta(seconds=round_seconds)
            # timer_str = (datetime(1970, 1, 1) + timer).strftime("%M:%S")
            #
            # # Update label
            # round_timer_label.config(text=timer_str)

            print(round_seconds)

            # Delays the program one second
            time.sleep(1)
            round_seconds -= 1

        sound_thread.join()

        # Start of rest round
        sound_thread = threading.Thread(target=play_sound, args=(ding,))
        sound_thread.start()

        rest_seconds = int(rest_input.get())

        # Work round
        while rest_seconds > 0:
            # Timer represents time left on countdown
            # timer = timedelta(seconds=rest_seconds)
            # timer_str = (datetime(1970, 1, 1) + timer).strftime("%M:%S")
            #
            # # Update label
            # round_timer_label.configure(text=timer_str)
            # print(timer_str)
            print(rest_seconds)

            # Delays the program one second
            time.sleep(1)
            rest_seconds -= 1

        sound_thread.join()

        rounds -= 1

    play_sound(ding)

# def start():
#     rounds = int(round_input.get())
#
#     while rounds > 0:
#
#         # Method for rest
#         work()
#
#         # Method for rest
#         rest()
#
#         rounds -= 1
#
#     play_sound(ding)
#
#
# def work():
#     print("work")
#
#
# def rest():
#     rest_seconds = int(rest_input.get())
#     print("rest")
#
#     def update_label():
#         nonlocal rest_seconds
#
#         if rest_seconds > 0:
#             timer = timedelta(seconds=rest_seconds)
#             timer_str = (datetime(1970, 1, 1) + timer).strftime("%M:%S")
#
#             # Update label
#             round_timer_label.configure(text=timer_str)
#
#             rest_seconds -= 1
#
#             # Schedule the update after 1000 milliseconds (1 second)
#             round_timer_label.after(1000, update_label)
#
#     # Initial call to start the timer
#     update_label()


def play_sound(sound):
    play(sound)


window = Tk()
window.title("Boxing App")
window.minsize(width=1300, height=800)

# Timer Label
round_timer_label = Label(text="Round Timer", font=FONT)
round_timer_label.grid(row=0, column=1)
# round_timer_label.config(padx=10)

# Round number input
round_input = Entry()
round_input.grid(row=1, column=0)
# round_input.insert(END, "Enter number of rounds.")
round_input.insert(END, "3")

# Round timer input
work_input = Entry()
work_input.grid(row=1, column=1)
# work_input.insert(END, "Enter round time (s).")
work_input.insert(END, "30")

# Rest timer input
rest_input = Entry()
rest_input.grid(row=1, column=2)
# rest_input.insert(END, "Enter rest time (s).")
rest_input.insert(END, "30")

# Timer Label
round_timer_label = Label(text="00:00", font=FONT)
round_timer_label.grid(row=2, column=1)
round_timer_label.config(padx=10)

# Start button
start_button = Button(text="Start Timer", font="bold", command=start)
start_button.grid(row=3, column=1)

window.mainloop()
