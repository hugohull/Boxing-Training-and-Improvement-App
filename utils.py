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

quotes = [
    "The successful warrior is the average man, with laser-like focus. - Bruce Lee",
    "It's not whether you get knocked down; it's whether you get up. - Vince Lombardi",
    "The more you sweat in training, the less you bleed in combat. - Navy SEALs Proverb",
    "I fear not the man who has practiced 10,000 kicks once, but I fear the man who has practiced one kick 10,"
    "000 times. - Bruce Lee",
    "A champion is someone who gets up when he can’t. - Jack Dempsey",
    "Everyone has a plan until they get punched in the mouth. - Mike Tyson",
    "It isn’t the mountains ahead to climb that wear you out; it’s the pebble in your shoe. - Muhammad Ali",
    "Adapt what is useful, reject what is useless, and add what is specifically your own. - Bruce Lee",
    "Victory is reserved for those who are willing to pay its price. - Sun Tzu",
    "To be a martial artist means to be an artist of life. - Bruce Lee",
    "He who is taught only by himself has a fool for a master. - Hunter S. Thompson",
    "Knowledge will give you power, but character respect. - Bruce Lee",
    "The fight is won or lost far away from witnesses, behind the lines, in the gym, and out there on the road, "
    "long before I dance under those lights. - Muhammad Ali",
    "There is no losing in jiu-jitsu. You either win or you learn. - Carlos Gracie Jr.",
    "If you know the way broadly you will see it in everything. - Miyamoto Musashi",
    "Martial arts is not about fighting; it’s about building character. - Bo Bennett",
    "One defeats a lot of people physically, but one wins over many more through mental conquest. - Jigoro Kano",
    "The path of martial arts begins and ends with courtesy. So be genuinely polite on every occasion. - Morihei "
    "Ueshiba",
    "In the confrontation between the stream and the rock, the stream always wins - not through strength but by "
    "perseverance. - H. Jackson Brown",
    "You must understand that there is more than one path to the top of the mountain. - Miyamoto Musashi",
    "Only in the midst of challenging moments do you find your inner strength. - Anderson Silva",
    "When you aim for perfection, you discover it's a moving target. - Georges St-Pierre",
    "True champions aren’t always the ones that win, but those with the most guts. - Mia Hamm",
    "The greatest victory is that which requires no battle. - Sun Tzu",
    "The more difficult the victory, the greater the happiness in winning. - Pelé",
    "Practice does not make perfect. Only perfect practice makes perfect. - Vince Lombardi",
    "The true science of martial arts means practicing them in such a way that they will be useful at any time. - Miyamoto Musashi",
    "Flow with whatever may happen and let your mind be free. - Zhuangzi",
    "The hardest battle you will ever have to fight is between who you are now and who you want to be. - Anonymous",
    "It does not matter how slowly you go as long as you do not stop. - Confucius",
    "Beware of the man who does not return your blow: he neither forgives you nor allows you to forgive yourself. - Bernard Shaw",
    "Do not pray for an easy life, pray for the strength to endure a difficult one. - Bruce Lee",
    "If you do not control the enemy, the enemy will control you. - Miyamoto Musashi",
    "Courage is not the absence of fear, but the triumph over it. - Nelson Mandela",
    "To be a great champion you must believe you are the best. If you’re not, pretend you are. - Muhammad Ali",
    "There are no limits. There are plateaus, but you must not stay there, you must go beyond them. - Bruce Lee",
    "You must not fight too often with one enemy, or you will teach him all your art of war. - Napoleon Bonaparte",
    "Pain is temporary. It may last a minute, or an hour, or a day, or a year, but eventually it will subside and something else will take its place. - Lance Armstrong",
    "The key to immortality is first living a life worth remembering. - Bruce Lee",
    "Fall seven times, stand up eight. - Japanese Proverb",
    "Do not be struck by others. Do not strike others. The goal is peace without incident. - Chojun Miyagi",
    "I am not a product of my circumstances. I am a product of my decisions. - Stephen Covey",
    "You can’t connect the dots looking forward; you can only connect them looking backwards. - Steve Jobs",
    "It’s not the size of the dog in the fight, it’s the size of the fight in the dog. - Mark Twain",
    "An insincere and evil friend is more to be feared than a wild beast; a wild beast may wound your body, but an evil friend will wound your mind. - Buddha",
    "No one is born a great cook, one learns by doing. - Julia Child",
    "You just can’t beat the person who never gives up. - Babe Ruth",
    "Keep your friends close, but your enemies closer. - Sun Tzu",
    "What you leave behind is not what is engraved in stone monuments, but what is woven into the lives of others. - Pericles",
    "The only difference between the impossible and the possible lies in a man’s determination. - Tommy Lasorda",
    "A good fighter is never aggressive; a good fighter never gets angry. - Lao Tzu",
    "Knowing others is intelligence; knowing yourself is true wisdom. Mastering others is strength; mastering yourself is true power. - Lao Tzu",
    "The fight is won or lost far away from witnesses - behind the lines, in the gym, and out there on the road, long before I dance under those lights. - Muhammad Ali",
    "There is no such thing as defeat until you admit it. - George Patton",
    "The ultimate aim of martial arts is not having to use them. - Miyamoto Musashi",
    "One should not focus on winning or losing but on achieving correctness and propriety in one's actions. - Gichin Funakoshi",
    "Only the disciplined ones in life are free. - Eliud Kipchoge",
    "A samurai must remain calm at all times even in the face of danger. - Chris Bradford",
    "Discipline is remembering what you want. - David Campbell",
    "Every defeat is a lesson. - Renzo Gracie",
    "Do not count the days; make the days count. - Muhammad Ali",
    "If you even dream of beating me, you'd better wake up and apologize. - Muhammad Ali",
    "To know oneself is to study oneself in action with another person. - Bruce Lee",
    "The only limit to our realization of tomorrow will be our doubts of today. - Franklin D. Roosevelt",
    "When you’re good at something, you’ll tell everyone. When you’re great at something, they’ll tell you. - Walter Payton",
    "Obstacles are things a person sees when he takes his eyes off his goal. - E. Joseph Cossman",
    "Do not let the behavior of others destroy your inner peace. - Dalai Lama",
    "It's not the daily increase but daily decrease. Hack away at the unessential. - Bruce Lee",
    "A wise man can learn more from a foolish question than a fool can learn from a wise answer. - Bruce Lee",
    "You must not only aim right, but draw the bow with all your might. - Henry David Thoreau",
    "The more we value things, the less we value ourselves. - Bruce Lee",
    "The spirit, the will to win, and the will to excel are the things that endure. - Vince Lombardi",
    "The measure of who we are is what we do with what we have. - Vince Lombardi",
    "Strength does not come from winning. Your struggles develop your strengths. - Arnold Schwarzenegger",
    "It's not bragging if you can back it up. - Muhammad Ali",
    "A man who has no imagination has no wings. - Muhammad Ali",
    "Mistakes are always forgivable, if one has the courage to admit them. - Bruce Lee",
    "I don’t count my sit-ups; I only start counting when it starts hurting because they’re the only ones that count. - Muhammad Ali",
    "Never interrupt your enemy when he is making a mistake. - Napoleon Bonaparte",
    "It's lack of faith that makes people afraid of meeting challenges, and I believed in myself. - Muhammad Ali",
    "You cannot swim for new horizons until you have courage to lose sight of the shore. - William Faulkner",
    "Always be yourself, express yourself, have faith in yourself, do not go out and look for a successful personality and duplicate it. - Bruce Lee",
    "If you spend too much time thinking about a thing, you'll never get it done. - Bruce Lee",
    "It is not sufficient to see and to know the beauty of a work. We must feel and be affected by it. - Voltaire",
    "What you are as a person is far more important than what you are as a basketball player. - John Wooden",
    "A hero is someone who understands the responsibility that comes with his freedom. - Bob Dylan",
    "What counts is not necessarily the size of the dog in the fight - it’s the size of the fight in the dog. - Dwight D. Eisenhower",
    "You have to believe in yourself when no one else does – that makes you a winner right there. - Venus Williams",
    "It’s not the will to win that matters—everyone has that. It’s the will to prepare to win that matters. - Paul \"Bear\" Bryant",
    "Real living is living for others. - Bruce Lee",
    "What does not kill me, makes me stronger. - Friedrich Nietzsche",
    "He who conquers himself is the mightiest warrior. - Confucius",
    "The more you find out about the world, the more opportunities there are to laugh at it. - Bill Nye",
    "Even the greatest was once a beginner. Don't be afraid to take that first step. - Muhammad Ali",
    "Courage, above all things, is the first quality of a warrior. - Carl von Clausewitz",
    "Winning is not everything, but wanting to win is. - Vince Lombardi",
    "You have to expect things of yourself before you can do them. - Michael Jordan",
    "The more you praise and celebrate your life, the more there is in life to celebrate. - Oprah Winfrey",
    "A champion is defined not by their wins but by how they can recover when they fall. - Serena Williams",
    "Some warriors look fierce, but are mild. Some seem timid, but are vicious. Look beyond appearances; position yourself for the advantage. - Deng Ming-Dao"
]


def get_quote():
    return random.choice(quotes)


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
