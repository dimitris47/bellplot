"""
Copyright 2024 Dimitris Psathas <dimitrisinbox@gmail.com>
This file is part of BellPlot.

BellPlot is free software: you can redistribute it and/or modify it under the
terms of the GNU General Public License  as  published by  the  Free Software
Foundation,  either version 3 of the License,  or (at your option)  any later
version.

BellPlot is distributed in the hope that it will be useful,  but  WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
A PARTICULAR PURPOSE.  See the  GNU General Public License  for more details.

You should have received a copy of the  GNU General Public License along with
BellPlot. If not, see <http://www.gnu.org/licenses/>.
"""


import sys
from PySide6 import QtWidgets
from mainwidget import MainWidget


def main():
    app = QtWidgets.QApplication()
    app.setApplicationName('Bell Plot')
    app.setApplicationDisplayName('Bell Plot')
    app.setOrganizationName('DP Software')
    app.setOrganizationDomain('com.dpsoftware.com')
    app.setApplicationVersion('0.99')

    w = app.primaryScreen().size().width()
    h = app.primaryScreen().size().height()
    window = MainWidget(w, h)
    window.setWindowTitle('Bell Plot')
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
