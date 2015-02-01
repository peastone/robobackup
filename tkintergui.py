from tkinter import filedialog, messagebox, Frame, PhotoImage, Label, \
        Text, Button, LEFT, RIGHT, YES, END
import os

class BackupGuiTk(Frame):
    def __init__(self, method, master=None, ask=False):
        self.picframe = Frame.__init__(self, master, width=100, height=100)
        self.image = PhotoImage()
        self.image["file"] = os.path.join("resources", "ASK.png")
        self.piclabel = Label(self.picframe, image=self.image)
        self.piclabel.pack()
        self.pack()
        self.logframe = Frame.__init__(self, master)
        self.label = Label(self.logframe)
        self.label.pack(fill = "both")
        self.loglabel = Label(self.logframe, text = "Log:")
        self.loglabel.pack(fill = "both")
        self.text = Text(self.logframe, width=10, height=10)
        self.text.pack(fill = "both")
        self.pack()
        self.buttonframe = Frame.__init__(self, master)
        self.save = Button(self.buttonframe, text = _("Save"), command=self.saveLog)
        self.save.pack(side=LEFT, fill = "both", expand=YES)
        self.close = Button(self.buttonframe, text = _("Close"), command=exit)
        self.close.pack(side=RIGHT, fill = "both", expand=YES)
        self.pack()
        self.master.title("Robobackup")
        self.startnow = True
        if ask:
            self.startnow = messagebox.askyesno("Robobackup",_("Start Backup now?"))
        if (self.startnow):
            self.image["file"] = os.path.join("resources", "BACKUP.png")
            method(self)
        self.mainloop()
    def setBackupSuccess(self):
        self.label["text"] = _("Success")
        self.label["bg"] = "green"
        self.image["file"] = os.path.join("resources", "SUCCESS.png")
    def setBackupFailure(self):
        self.label["text"] = _("Failure")
        self.label["bg"] = "red"
        self.image["file"] = os.path.join("resources", "FAIL.png")
    def setBackupCheck(self):
        self.label["text"] = _("Check backup")
        self.label["bg"] = "orange"
        self.image["file"] = os.path.join("resources", "CHECK.png")
    def setLog(self, log):
        self.text.insert(END, log)
    def saveLog(self):
        filedialog
        f = filedialog.asksaveasfile(mode='w', filetypes=[(_("Text files"), "*.txt")])
        if f is None:
            return
        log = str(self.text.get(1.0,END))
        try:
            f.write(log)
            f.close()
        except:
            print("Error writing logfile from GUI")