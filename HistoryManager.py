import json


def load_punch_history():
    try:
        with open('history/punch_history.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return a default dictionary if there's an error loading the file
        return {
            'Total Punches': 0,
            'Total Left': 0,
            'Total Right': 0,
            'Total Head': 0,
            'Total Body': 0,
            'Left Head': 0,
            'Left Body': 0,
            'Right Head': 0,
            'Right Body': 0,
            'Completed Rounds': 0,
            'Correct Combinations': 0,
            'Incorrect Combinations': 0,
            'Games Won': 0,
            'Games Lost': 0,
            'Games Drawn': 0
        }


def get_punch_history():
    return load_punch_history()


def save_punch_history(history):
    with open('history/punch_history.json', 'w') as file:
        json.dump(history, file)


def reset_punch_history():
    default_history = {
        'Total Punches': 0,
        'Total Left': 0,
        'Total Right': 0,
        'Total Head': 0,
        'Total Body': 0,
        'Left Head': 0,
        'Left Body': 0,
        'Right Head': 0,
        'Right Body': 0,
        'Completed Rounds': 0,
        'Correct Combinations': 0,
        'Incorrect Combinations': 0,
        'Games Won': 0,
        'Games Lost': 0,
        'Games Drawn': 0
    }

    with open('history/punch_history.json', 'w') as file:
        json.dump(default_history, file)

    load_punch_history()
