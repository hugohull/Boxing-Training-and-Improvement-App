from tkinter import *
import threading
from pydub import AudioSegment
from pydub.playback import play
from punch_tracker import run_punch_tracker

FONT = ("Calibri", 14)
ding = AudioSegment.from_mp3("Audio/Boxing Bell Sound.mp3")


def start():
    global rounds
    rounds = int(round_input.get())
    start_work()  # Start first work round


def play_sound():
    # Using a thread to avoid blocking the GUI while playing sound
    threading.Thread(target=lambda: play(ding), daemon=True).start()


def update_timer(seconds, type='work'):
    if seconds > 0:
        timer_str = f"{seconds // 60:02d}:{seconds % 60:02d}"
        round_timer_label.config(text=timer_str)
        # print(seconds)
        window.after(1000, update_timer, seconds - 1, type)
    else:
        if type == 'work':
            # Transition to rest period, play sound to indicate start
            play_sound()
            start_rest()
        else:
            # End of rest period, check if there are more rounds
            next_round()


def start_rest():
    rest_seconds = int(rest_input.get())
    # No need to play sound here, it's already played at transition
    update_timer(rest_seconds, 'rest')


def start_work():
    round_seconds = int(work_input.get())
    # Play sound to indicate the start of work round
    play_sound()
    update_timer(round_seconds, 'work')


def next_round():
    global rounds
    rounds -= 1
    if rounds > 0:
        start_work()  # Start next work round
    else:
        # All rounds completed, play sound to indicate end of session
        play_sound()
        round_timer_label.config(text="Done!")


def start_timer_and_video():
    # Start the timer in a separate thread
    # threading.Thread(target=start, daemon=True).start()
    # Start the video tracking in a separate thread
    run_punch_tracker()
    start()


window = Tk()
window.title("Boxing App")
window.minsize(width=854, height=480)

# Timer Label
round_timer_label = Label(text="Round Timer", font=FONT)
round_timer_label.grid(row=0, column=1)

# Round number input
round_input = Entry(window)
round_input.grid(row=1, column=0, padx=(140, 0o1))
# round_input.insert(END, "Enter number of rounds.")
round_input.insert(END, "3")

# Round timer input
work_input = Entry(window)
work_input.grid(row=1, column=1)
# work_input.insert(END, "Enter round time (s).")
work_input.insert(END, "30")

# Rest timer input
rest_input = Entry(window)
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

start_with_video_button = Button(text="Start Timer With Video", font="bold", command=start_timer_and_video)
start_with_video_button.grid(row=4, column=1)

window.mainloop()
