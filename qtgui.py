"""
Qt GUI for Robobackup
This file is part of Robobackup.
Copyright 2015 Siegfried Schoefer

Robobackup is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Robobackup is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.Qt import QPixmap
from PyQt5.QtWidgets import QMessageBox
from logtools import Severity, logbook
import os

class BackupGuiQt(QtWidgets.QWidget):
    """
    The main widget of the robobackup GUI made with Qt.
    """
    def __init__(self, method, *args, **kwargs):
        super(BackupGuiQt, self).__init__(*args, **kwargs)
        self._method_ = method
        self._gui_ = uic.loadUi(os.path.join(os.path.dirname(\
            os.path.relpath(__file__)), "ui", "robobackup-gui.ui"), \
            self)
        self.__set_image("ASK.png")
        self._gui_.btnStart.setText(_("Start Backup"))
        self._gui_.btnClose.setText(_("Close"))
        self.__set_status("")
        self._gui_.clockLabel.setText(_("Elapsed time:"))
        self._gui_.logLabel.setText(_("Log:"))
        self._gui_.btnStart.clicked.connect(self.__clk)
        self._gui_.btnClose.clicked.connect(self.__cls)
        self._timer_ = QtCore.QTimer()
        self._timer_.timeout.connect(self.__show_time)
        self._timer_.start(1000)
        self._time_ = QtCore.QTime()

    @pyqtSlot()
    def __clk(self):
        """
        This method starts the backup. It is a slot which is connected
        to the signal "click" of the button "btnStart".
        """
        try:
            self._gui_.btnStart.setEnabled(False)
            self._gui_.btnClose.setEnabled(False)
            self._time_.start()
            self._method_()
            self._timer_.timeout.disconnect(self.__show_time)
            self._gui_.btnClose.setEnabled(True)
        except:
            QMessageBox.critical(self, _("Critical"), \
            _("Robobackup failed. Contact your admin."), \
            QMessageBox.Ok)
            self._timer_.timeout.disconnect(self.__show_time)
            self._gui_.btnClose.setEnabled(True)

    @pyqtSlot()
    def __cls(self):
        """
        This method is used to close the GUI. It is a slot which is
        connected to the signal "click" of the button "btnClose".
        """
        self.close() # pylint: disable=maybe-no-member

    @pyqtSlot()
    def __show_time(self):
        """
        The digital timer gets incremented.
        """
        milliseconds = self._time_.elapsed()
        seconds, milliseconds = divmod(milliseconds, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        digitalclock = "{hh:02d}:{mm:02d}:{ss:02d}".format(hh=hours, \
            mm=minutes, ss=seconds)
        self._gui_.lcd.display(digitalclock)

    def update(self):
        """
        This method will be called, if logs are changing.
        """
        color = logbook.get_severity()
        self.__set_color(color.name)
        self._gui_.log.setText(logbook.get_string())
        if color is Severity.green:
            self.__set_image("SUCCESS.png")
            self.__set_status(_("Success"))
        elif color is Severity.orange:
            self.__set_image("CHECK.png")
            self.__set_status(_("Check backup"))
        elif color is Severity.red:
            self.__set_image("FAIL.png")
            self.__set_status(_("Failure"))
        else:
            raise RuntimeError(_("Color does not match an action."))

    def __set_image(self, img):
        """
        This method is used to set memorizable images to illustrate
        the status of the programm.
        """
        self._gui_.statusPicture.setPixmap(QPixmap(os.path.join \
            (os.path.dirname(os.path.relpath(__file__)), "resources",\
            img)))

    def __set_status(self, status):
        """
        This method is used to set the text of a short label indicating
        the status of robobackup.
        """
        self._gui_.errorLabel.setText(status)

    def __set_color(self, color):
        """
        This method is used to set the colour of a field.
        It can be used to signal a critical error with red.
        """
        self._gui_.errorLabel.setStyleSheet(\
            "QLabel { background-color: " + color +"}")
