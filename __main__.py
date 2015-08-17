#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Robobackup is a tool for automating backups.
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
import os, sys
import gettext
import locale
import time, datetime
from logtools import logbook, Level
try:
    from qtgui import BackupGuiQt
    from PyQt5 import QtWidgets
    qt = True
except ImportError:
    import tkintergui
    qt = False
from robobackup import backup
import tkinter, tkinter.messagebox
import signal

# pylint: disable=invalid-name
if __name__ == "__main__":
    try:
        # enable CTRL+C on the command line even if Qt runs
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        # setup the logging system
        # generate a log file with the latest date in its name in
        # the subfolder "logs"
        TIMESTAMP = datetime.datetime.fromtimestamp(time.time()).\
            strftime('%Y-%m-%d_%H-%M-%S')
        LOGDIR = os.path.join(os.path.dirname(\
            os.path.relpath(__file__)), "logs")
        if not os.path.exists(LOGDIR):
            # If an error occurs making the directory,
            # one will not be able to log errors to a file.
            # This will cause the program to fail (an exception will be
            # thrown) and a messagebox will be displayed.
            os.makedirs(LOGDIR)
        LOGFILE = os.path.join(LOGDIR, "robobackup" + TIMESTAMP + \
            os.extsep + "txt")
        logbook.set_logfile(LOGFILE)
        logbook.set_level(Level.DEBUG)

        # install translation
        if sys.platform.startswith('win'):
            if os.getenv('LANG') is None:
                lang, _ = locale.getdefaultlocale()
                os.environ['LANG'] = lang
        gettext.install("robobackup", os.path.join(os.path.dirname(os.path.relpath(__file__)), "locale"))

        # Some people want to click the start button on the GUI
        # so that they can control the time when the backup is started.
        # Other people want to use the program as scheduled task
        # without a GUI (--nogui option on the command line).
        startgui = True
        if len(sys.argv) == 2:
            if sys.argv[1] == "--nogui":
                startgui = False

        if startgui:
            if qt:
                qtapp = QtWidgets.QApplication(sys.argv)
                widget = BackupGuiQt(method=backup)
                logbook.register_observer(widget)
                widget.show() # pylint: disable=no-member
                sys.exit(qtapp.exec_())
            else:
                widget = tkintergui.BackupGuiTk(method=backup)
                logbook.register_observer(widget)
                widget.mainloop()
        else:
            backup()

    except SystemExit:
        # SystemExit is fired, when exit is called. This can happen by
        # Qt. In this case it is intended.
        pass
    except:
        # Would show a messagebox, if an exception was catched,
        # which was not registered in a logbook.
        # This would happen, if a log file could not be stored.
        tkwindowroot = tkinter.Tk()
        # hide the Tk root window
        tkwindowroot.withdraw()
        tkinter.messagebox.showinfo(_("Critical"), _("Robobackup " \
            "failed. Contact your admin."))
        raise
