# Boxing App README

The boxing app that uses the webcam to provide punch tracking and training to the user.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Requirements](#requirements)
- [File List](#file-list)

## Installation

### Prerequisites

Make sure to have the following installed before proceeding:
- **Operating System**: Developed and tested only on macOS Version 14.4.1
- **Python 3.8 or higher** 
- **Additional dependencies**: (listed below)

### Installing from Source

1. Clone the repository or download the source code:
    git clone https://campus.cs.le.ac.uk/gitlab/ug_project/23-24/hh280
    cd hh280
2. Install dependencies:
   - pip install PyQt5
   - pip install PyQtChart 
   - pip install pyqtgraph
   - pip install pydub
   - pip install opencv-python
   - pip install opencv-contrib-python
   - pip install gtts
   - pip install playsound
3. Open in IDE and run main.py.

### Installing from Archive file

1. Download archive (zip) file.
2. Unzip file
3. Install dependencies:
   - pip install PyQtChart 
   - pip install PyQt5
   - pip install PyQtChart 
   - pip install pyqtgraph
   - pip install pydub
   - pip install opencv-python
   - pip install opencv-contrib-python
   - pip install gtts
   - pip install playsound
4. Open in IDE and run main.py.

## Usage

To run the software, run main.py in a IDE of your choice. It was developed using PyCharm professional in macOS. 

**Note:** You may also have to give your IDE permissions to use your webcam.


## Requirements

This software requires:
- **Operating System**: Has only been tested on macOS.
- **Hardware Requirements**: A PC that can run a simple Python programme.

## File List

- `main.py` - Main executable file.
- `HistoryManager.py` - The file responsible for the user's history.
- `ImageLabel.py` - The file responsible for controlling the overlays on the punch tracking window. 
- `MainWindow.py` - The file responsible for manging the Applications general GUI.
- `punch_tracker.py` - The file containing the methods responsible for tracking punches.
- `styles.py` - A file containing the file for button styles.
- `utils.py` - A file responsible for general methods that provide functionality to the application.
- `VideoThread.py` - The file responsible for managing the threads of the methods to track punches.
- `punch_history.json` - The JSON that holds the user's personal punch tracking history.

