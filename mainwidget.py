import datetime
import os
from io import BytesIO

import matplotlib.pyplot as plt
import numpy as np
import scipy.stats
from PIL import Image
from PySide6.QtCore import Qt, QLocale, Slot
from PySide6.QtGui import QPixmap, QIcon, QDoubleValidator, QImage
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QPushButton,
    QHBoxLayout, QCheckBox, QSizePolicy, QMessageBox, QFileDialog
)


class MainWidget(QWidget):
    def __init__(self, w, h):
        super().__init__()
        self.screen_width, self.screen_height = w, h
        self.init_hor = int(w / 2 - self.width() / 2)
        self.resize(316, 224)
        self.setWindowIcon(QIcon('bellplot.png'))
        self.box = QVBoxLayout(self)

        form = QFormLayout()
        labels = ['Mean', 'Deviation', 'Score', 'Cumulative probability']
        self.entries = {}
        validator = QDoubleValidator()
        validator.setNotation(QDoubleValidator.StandardNotation)
        validator.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        for label in labels:
            lbl = QLabel(label)
            entry = QLineEdit()
            entry.setValidator(validator)
            entry.setAlignment(Qt.AlignCenter)
            entry.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
            entry.returnPressed.connect(self.calculation)
            form.addRow(lbl, entry)
            self.entries[label] = entry
        self.box.addLayout(form)

        action_row = QHBoxLayout()
        self.calc_btn = QPushButton('Calculate')
        self.calc_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.calc_btn.clicked.connect(self.calculation)
        self.check_box = QCheckBox()
        action_row.addStretch(32)
        action_row.addWidget(self.calc_btn)
        action_row.addWidget(QLabel('Plot'))
        action_row.addWidget(self.check_box)
        action_row.addStretch(32)
        self.box.addLayout(action_row)

        self.plot_lbl = QLabel()
        self.plot_lbl.setVisible(False)
        self.save_btn = QPushButton('Save figure')
        self.save_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        self.save_btn.setVisible(False)
        self.save_btn.clicked.connect(self.save_image)
        self.box.addWidget(self.plot_lbl)
        self.box.addWidget(self.save_btn, alignment=Qt.AlignCenter)
        self.move(self.init_hor, 96)

    @Slot()
    def calculation(self):
        mean, dev = self.entries['Mean'].text(), self.entries['Deviation'].text()
        if mean and dev:
            mean, dev = float(mean), float(dev)
            score, prob = self.entries['Score'].text(), self.entries['Cumulative probability'].text()
            if not score and prob:
                prob, score = float(prob), scipy.stats.norm.ppf(float(prob), mean, dev)
                self.entries['Score'].setText(str(round(score, 1)))
            elif not prob and score:
                score, prob = float(score), scipy.stats.norm.cdf(float(score), mean, dev)
                self.entries['Cumulative probability'].setText(str(round(prob, 5)))
            else:
                self.show_warning('Only one out of 4 values must be left empty.')
                return
            self.determine_plotting(mean, dev, score, prob)
        else:
            self.show_warning('Both the mean and deviation entries must be filled.')

    def determine_plotting(self, mean, dev, score, prob):
        if self.check_box.isChecked():
            self.plot_bell(mean, dev, score, prob)
        else:
            self.remove_plot_elements()

    def remove_plot_elements(self):
        for widget in [self.plot_lbl, self.save_btn]:
            widget.setVisible(False)
            self.box.removeWidget(widget)
        self.resize(316, 224)
        self.move(self.init_hor, 96)
        self.adjustSize()

    def show_warning(self, message):
        QMessageBox.warning(self, 'Wrong input', message)
        self.remove_plot_elements()

    def plot_bell(self, mean, dev, score, prob):
        z = (score - mean) / dev
        x_all = np.linspace(-10, 10, 20000)
        y_all = scipy.stats.norm.pdf(x_all, 0, 1)
        fig, ax = plt.subplots(figsize=(9, 7))
        ax.plot(x_all, y_all)
        ax.fill_between(x_all, y_all, alpha=0.1)
        ax.fill_between(x_all[x_all <= z], y_all[x_all <= z], alpha=0.3, color='b')
        ax.plot(z, scipy.stats.norm.pdf(z, 0, 1), 'ro')
        ax.set_xlim(-4, 4)
        ax.set_xlabel(f'# of Std Devs: {abs(round(z, 2))}\nScore: {round(score, 1)}\nCumulative Probability: {round(prob, 5)}%')
        ax.set_yticklabels([])
        ax.set_title('Normal Gaussian Curve')
        plt.grid(True)
        self.plot_lbl.setPixmap(self.fig2pixmap(fig))
        self.plot_lbl.setVisible(True)
        self.save_btn.setVisible(True)
        self.box.addWidget(self.plot_lbl)
        self.box.addWidget(self.save_btn, alignment=Qt.AlignCenter)
        plt.close()
        self.move(int(self.screen_width / 2 - self.plot_lbl.width() / 2 - 24), 96)

    def fig2pixmap(self, fig):
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=900)
        buf.seek(0)
        img = Image.open(buf).convert('RGBA')
        qim = QImage(img.tobytes(), img.width, img.height, QImage.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qim)
        ratio = (self.screen_width / self.screen_height) * (9 / 7)
        return pixmap.scaled(int(self.screen_width * 0.56 * ratio), int(self.screen_height * 0.56), Qt.KeepAspectRatio,
                             Qt.SmoothTransformation)

    def save_image(self):
        default_path = os.path.join(os.path.expanduser('~'), 'Desktop',
                                    f'figure_{datetime.datetime.now().strftime("%Y%m%d_%H.%M")}.png')
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Figure', default_path, 'PNG Files (*.png);;All Files (*)')
        if filename:
            filename = filename if filename.endswith('.png') else f'{filename}.png'
            pixmap = self.plot_lbl.pixmap()
            if pixmap and pixmap.save(filename, 'PNG'):
                QMessageBox.information(self, 'Figure saved', 'Figure saved successfully')
            else:
                QMessageBox.warning(self, 'Failed to save', 'Failed to save figure')
