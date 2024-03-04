import sys
from PyQt5.QtWidgets import QApplication
from MainWindow import MainWindow


def main():
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
