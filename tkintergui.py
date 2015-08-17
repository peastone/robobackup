# -*- coding: utf-8 -*-

"""
This file is part of Robobackup.
Copyright 2014, 2015 Siegfried Schoefer

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
from tkinter import messagebox, Frame, PhotoImage, Label, \
        Text, Button, END
import os
import time
from logtools import Severity, logbook

class BackupGuiTk(Frame):
    """
    The main widget of the robobackup GUI made with tkinter.
    """
    def __init__(self, method=None, master=None):
        self.method = method
        self.picframe = Frame.__init__(self, master)
        self.master.title("Robobackup")
        self.image = PhotoImage()
        self.image["file"] = os.path.join(os.path.dirname(\
            os.path.relpath(__file__)), "resources", "ASK.png")
        self.piclabel = Label(self.picframe, image=self.image)
        self.piclabel.grid(row=0, column=0, columnspan=4, rowspan=6)
        self.clocklabel = Label(self.picframe, text=_("Elapsed time:"))
        self.clocklabel.grid(row=0, column=4, sticky="NSEW")
        self.clock = Label(self.picframe, text="")
        self.clock.grid(row=1, column=4, sticky="NSEW")
        self.start = Button(self.picframe, text=_("Start Backup"), command=self.__clk)
        self.start.grid(row=3, column=4, sticky="NSEW")
        self.errorlabel = Label(self.picframe)
        self.errorlabel.grid(row=4, column=4, sticky="NSEW")
        self.close = Button(self.picframe, text=_("Close"), command=self.__cls)
        self.close.grid(row=5, column=4, sticky="NSEW")
        self.loglabel = Label(self.picframe, text=_("Log:"), justify="left")
        self.loglabel.grid(row=6, column=0, columnspan=5, sticky="NSEW")
        self.text = Text(self.picframe)
        self.text.grid(row=7, column=0, rowspan=6, columnspan=5, sticky="NSEW")
        self.timeout = False
        self.starttime = -1
    def __clk(self):
        """
        This method starts the backup. It is a slot which is connected
        to the signal "click" of the button "btnStart".
        """
        self.start.config(state="disabled")
        self.close.config(state="disabled")
        self.clock_tick()
        try:
            self.method()
        except:
            if __debug__:
                logbook.exception("")
            self.set_backup_failure()
            messagebox.showinfo(_("Critical"), _("Robobackup " \
                "failed. Contact your admin."))
        finally:
            self.timeout = True
            self.close.config(state="normal")
    def __cls(self):
        """
        This method is used to close the GUI.
        """
        self.master.destroy()
    def clock_tick(self):
        """
        This is used to count the seconds the backup method runs.
        """
        if not self.timeout:
            self.starttime = int(time.time() * 1000)
        milliseconds = int(time.time() * 1000) - self.starttime
        seconds, milliseconds = divmod(milliseconds, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        digitalclock = "{hh:02d}:{mm:02d}:{ss:02d}".format(hh=hours, \
            mm=minutes, ss=seconds)
        self.clock.configure(text=digitalclock)
        if not self.timeout:
            self.master.after(1000, self.clock_tick)
    def update(self):
        """
        This method will be called, if logs are changing.
        """
        color = logbook.get_severity()
        self.set_log(logbook.get_string())
        if color is Severity.green:
            self.set_backup_success()
        elif color is Severity.orange:
            self.set_backup_check()
        elif color is Severity.red:
            self.set_backup_failure()
        else:
            raise RuntimeError(_("Color does not match an action."))
    def set_backup_success(self):
        """
        Set everything green.
        """
        self.errorlabel.configure(text=_("Success"))
        self.errorlabel["bg"] = "green"
        self.image["file"] = os.path.join(os.path.dirname(\
            os.path.relpath(__file__)), "resources", "SUCCESS.png")
    def set_backup_check(self):
        """
        Set everything orange.
        """
        self.errorlabel.configure(text=_("Check backup"))
        self.errorlabel["bg"] = "orange"
        self.image["file"] = os.path.join(os.path.dirname(\
            os.path.relpath(__file__)), "resources", "CHECK.png")
    def set_backup_failure(self):
        """
        Set everything red.
        """
        self.errorlabel.configure(text=_("Failure"))
        self.errorlabel["bg"] = "red"
        self.image["file"] = os.path.join(os.path.dirname(\
            os.path.relpath(__file__)), "resources", "FAIL.png")
    def set_log(self, log):
        """
        Write text to the GUI.
        """
        self.text.delete("1.0", END)
        self.text.insert(END, log)
