"""
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

import logging
from enum import Enum

class Severity(Enum):
    green = 0
    orange = 1
    red = 2

class Level(Enum):
    CRITICAL = logging.CRITICAL
    FATAL = logging.FATAL
    ERROR = logging.ERROR
    WARNING = logging.WARNING
    WARN = logging.WARN
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

class Logbook():
    """
    The class Logbook extends the standard python logging by counting
    the number of errors and warnings that have occured. Based on
    these findings, the severity of the logged problems is assessed.
    """
    def __init__(self, logger, logfile):
        self._num_warnings_ = 0
        self._num_errors_ = 0
        self._logger_ = logger
        self.logfile = logfile

        handler = logging.FileHandler(logfile)
        formatter = logging.Formatter(\
            "[%(levelname)s] (%(asctime)s) %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def setLevel(self, level):
        self._logger_.setLevel(level.value)

    def critical(self, msg):
        """
        Log a critical error, increase the error count and raise a
        RuntimeError.
        """
        self._num_errors_ += 1
        self._logger_.critical(msg)
        raise RuntimeError(msg)

    def error(self, msg):
        """
        Log an error and increase the error count.
        """
        self._num_errors_ += 1
        self._logger_.error(msg)

    def warning(self, msg):
        """
        Log a warning and increase the warnings count.
        """
        self._num_warnings_ += 1
        self._logger_.warning(msg)

    def info(self, msg):
        """
        Log an info.
        """
        self._logger_.info(msg)

    def debug(self, msg):
        """
        Log a debug message.
        """
        self._logger_.debug(msg)

    def exception(self, msg):
        """
        Logs an exception.
        This method should only be called from an exception handler.
        """
        self._logger_.exception(msg)

    def get_severity(self):
        """
        Get an error assessment. If there are no errors and warnings,
        the result will be "green". You will get an "orange" evaluation,
        if there are warnings only. A "red" evaluation will follow as
        soon as an error is counted.
        """
        ret = Severity.green
        if self._num_warnings_ > 0:
            ret = Severity.orange
        if self._num_errors_ > 0:
            ret = Severity.red
        return ret
