import sys
from PySide6 import QtWidgets
from mainwidget import MainWidget


def main():
    app = QtWidgets.QApplication()
    app.setApplicationName('Bell Plot')
    app.setApplicationDisplayName('Bell Plot')
    app.setOrganizationName('DP Software')
    app.setOrganizationDomain('com.dpsoftware.com')
    app.setApplicationVersion('0.1.0')

    w = app.primaryScreen().size().width()
    h = app.primaryScreen().size().height()
    window = MainWidget(w, h)
    window.setWindowTitle('Bell Plot')
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
