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

import multiprocessing
import logging

class Logbook():
    """
    The class Logbook extends the standard python logging by counting
    the number of errors and warnings that have occured. Based on
    these findings, the severity of the logged problems is assessed.
    """
    def __init__(self, logger, logfile):
        self._num_warnings_ = multiprocessing.Value('i', 0) # pylint: disable=no-member
        self._num_errors_ = multiprocessing.Value('i', 0) # pylint: disable=no-member
        self._logger_ = logger
        self.logfile = logfile
        self._lock_ = multiprocessing.Lock()

        handler = logging.FileHandler(logfile)
        formatter = logging.Formatter(\
            "[%(levelname)s] (%(asctime)s) %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    def critical(self, msg):
        """
        Log a critical error, increase the error count and raise a
        RuntimeError.
        """
        with self._num_errors_.get_lock():
            self._num_errors_.value += 1
            self._logger_.critical(msg)
        raise RuntimeError(msg)

    def error(self, msg):
        """
        Log an error and increase the error count.
        """
        with self._num_errors_.get_lock():
            self._num_errors_.value += 1
            self._logger_.error(msg)

    def warning(self, msg):
        """
        Log a warning and increase the warnings count.
        """
        with self._num_warnings_.get_lock():
            self._num_warnings_.value += 1
            self._logger_.warning(msg)

    def info(self, msg):
        """
        Log an info.
        """
        self._lock_.acquire()
        self._logger_.info(msg)
        self._lock_.release()

    def debug(self, msg):
        """
        Log a debug message.
        """
        self._lock_.acquire()
        self._logger_.debug(msg)
        self._lock_.release()

    def get_severity(self):
        """
        Get an error assessment. If there are no errors and warnings,
        the result will be "green". You will get an "orange" evaluation,
        if there are warnings only. A "red" evaluation will follow as
        soon as an error is counted.
        """
        ret = "green"
        if self._num_warnings_.value > 0:
            ret = "orange"
        if self._num_errors_.value > 0:
            ret = "red"
        return ret
