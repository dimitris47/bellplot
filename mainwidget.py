import datetime
import numpy as np
import scipy.stats
import os
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtWidgets import *
from PySide6.QtCore import QLocale
from io import BytesIO
from PIL import Image


class MainWidget(QtWidgets.QWidget):
    box: QVBoxLayout
    plot_lbl: QLabel
    save_btn: QPushButton
    screen_width: int
    screen_height: int

    def __init__(self, w, h):
        super().__init__()

        self.screen_width = w
        self.screen_height = h
        self.resize(316, 224)

        self.setWindowIcon(QIcon('bellplot.png'))
        self.box = QVBoxLayout(self)

        self.form = QFormLayout()
        self.mean_lbl = QLabel('Mean')
        self.mean_entry = QLineEdit()
        self.dev_lbl = QLabel('Deviation')
        self.dev_entry = QLineEdit()
        self.score_lbl = QLabel('Score')
        self.score_entry = QLineEdit()
        self.prob_lbl = QLabel('Cumulative probability')
        self.prob_entry = QLineEdit()

        validator = QtGui.QDoubleValidator()
        validator.setNotation(QtGui.QDoubleValidator.StandardNotation)
        validator.setLocale(QLocale(QLocale.Language.English, QLocale.Country.UnitedStates))

        for widget in [self.mean_entry, self.dev_entry, self.score_entry, self.prob_entry]:
            widget.setValidator(validator)
            widget.setAlignment(QtCore.Qt.AlignCenter)
            widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            widget.returnPressed.connect(self.calculation)

        for row in [[self.mean_lbl, self.mean_entry],
                    [self.dev_lbl, self.dev_entry],
                    [self.score_lbl, self.score_entry],
                    [self.prob_lbl, self.prob_entry]]:
            self.form.addRow(row[0], row[1])

        self.plot_lbl = QLabel('')
        self.plot_lbl.setVisible(False)

        self.calc_btn = QPushButton('Calculate')
        self.calc_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.calc_btn.clicked.connect(self.calculation)
        self.radio_lbl = QLabel('Plot')
        self.check_box = QCheckBox()
        self.check_box.setChecked(False)
        self.action_row = QHBoxLayout()
        for w in [self.calc_btn, self.radio_lbl, self.check_box]:
            self.action_row.addWidget(w)

        self.save_btn = QPushButton('Save figure')
        self.save_btn.setVisible(False)
        self.save_btn.clicked.connect(self.save_image)

        self.box.addLayout(self.form)
        self.box.addLayout(self.action_row)
        for widget in [self.plot_lbl, self.save_btn]:
            self.box.addWidget(widget)

        self.move(int(self.screen_width/2 - self.width()/2), 96)
        print(self.width())

    @QtCore.Slot()
    def calculation(self):
        self.plot_lbl.setVisible(False)
        self.resize(316, 224)
        if len(self.mean_entry.text()) and len(self.dev_entry.text()):
            mean = float(self.mean_entry.text())
            dev = float(self.dev_entry.text())
            if len(self.score_entry.text()) == 0 and len(self.prob_entry.text()) != 0:
                prob = float(self.prob_entry.text())
                score = scipy.stats.norm.ppf(prob, mean, dev)
                self.score_entry.setText(str(round(score, 1)))
                if self.check_box.isChecked():
                    self.plot_bell(mean, dev, score, prob)
            elif len(self.prob_entry.text()) == 0 and len(self.score_entry.text()) != 0:
                score = float(self.score_entry.text())
                prob = scipy.stats.norm.cdf(score, mean, dev)
                self.prob_entry.setText(str(round(prob, 5)))
                if self.check_box.isChecked():
                    self.plot_bell(mean, dev, score, prob)
            else:
                QMessageBox.warning(self, 'Wrong input', 'Only one out of 4 values must be left empty.')
                self.plot_lbl.setVisible(False)
        else:
            QMessageBox.warning(self, 'Wrong input', 'Both the mean and deviation entries must be filled.')
            self.plot_lbl.setVisible(False)

    def plot_bell(self, mean, dev, score, prob):
        import matplotlib.pyplot as plt

        z1 = (mean - score) / dev
        z2 = (score - mean) / dev

        x = np.arange(z1, z2, 0.001)
        x_all = np.arange(-10, 10, 0.001)
        y = scipy.stats.norm.pdf(x, 0, 1)
        y2 = scipy.stats.norm.pdf(x_all, 0, 1)

        fig, ax = plt.subplots(figsize=(9, 7))
        ax.plot(x_all, y2)

        ax.fill_between(x, y, 0, alpha=0.3, color='b')
        ax.fill_between(x_all, y2, 0, alpha=0.1)
        ax.set_xlim([-4, 4])
        ax.set_xlabel(f'# of Standard Deviations Outside the Mean: {abs(round((score - mean) / dev, 2))}\n'
                      f'Score: {round(score, 1)}\nCumulative Probability: {round(prob, 3)}% -- 1/{round(1/(1-prob))}')
        ax.set_yticklabels([])
        ax.set_title('Normal Gaussian Curve')

        plt.grid(True)

        self.plot_lbl.setVisible(True)
        self.plot_lbl.setScaledContents(True)
        self.plot_lbl.setPixmap(self.fig2pixmap(fig))
        self.save_btn.setVisible(True)

        plt.close()

        self.move(int(self.screen_width/2 - self.width()/2), 96)

    def fig2pixmap(self, fig):
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=900)
        buf.seek(0)
        img = Image.open(buf)
        qim = QtGui.QImage(img.tobytes(), img.size[0], img.size[1], QtGui.QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qim)
        w = self.screen_width
        h = self.screen_height
        ratio = w / h * 9 / 7
        return pixmap.scaled(int(w * 0.56 * ratio), int(h * 0.56), QtCore.Qt.KeepAspectRatio,
                             QtCore.Qt.SmoothTransformation)

    def save_image(self):
        default_dir = os.path.expanduser('~') + '/Desktop'
        default_filename = os.path.join(default_dir, f'figure_{datetime.datetime.now().strftime("%Y%m%d_%H.%M")}.png')
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self,
                                                  'Save Figure',
                                                  default_filename,
                                                  'PNG Files (*.png);;All Files (*)',
                                                  options=options)
        if filename:
            if not filename.endswith('.png'):
                filename += '.png'
            pixmap = self.plot_lbl.pixmap()
            if pixmap:
                pixmap.save(filename, 'PNG')
                QMessageBox.information(self, 'Figure saved', 'Figure saved successfully')
            else:
                QMessageBox.warning(self, 'Failed to save', 'Failed to save figure')
