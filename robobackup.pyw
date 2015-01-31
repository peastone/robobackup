from defusedxml.ElementTree import parse
from subprocess import call
from subprocess import check_output
from os.path import isdir
from os.path import isfile
from datetime import date
import os
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import gettext

class BackupApp(Frame):
    def __init__(self, master=None, ask=False):
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
            backup(self)
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

class Log():
    def __init__(self):
        self.log = "===\r\n"
        self.orange = False
    def append(self, msg):
        self.log = self.log + msg + "\r\n===\r\n"
    def getLog(self):
        return self.log
    def setLogOrange(self):
        self.orange = True
    def getLogOrange(self):
        return self.orange

def fatal(app, msg):
    app.setBackupFailure()
    app.setLog(msg)
    app.mainloop()

def strip(s):
    if s != None:
        return s.rstrip().lstrip()
    else:
        return ''

def executeShellCommand(c, app):
    res = 0
    try:
        res = call(c, shell=True)
        if res != 0:
            raise Exception("error")
    except:
        fatal(app,"FATAL: " + c + " RETURN VALUE: " + str(res))

def executeRobocopy(c, errorlevel, app):
    res = 0
    try:
        res = call(c, shell=True)
        if res >= errorlevel:
            raise Exception("error")
    except:
        fatal(app,"FATAL: " + c + " RETURN VALUE: " + str(res))

def getDeviceNames(app):
    t1 = ""
    try:
        t1 = check_output("wmic logicaldisk get caption, volumename", shell = True, universal_newlines = True)
    except:
        fatal(app,"wmic logicaldisk get caption, volumename failed")
    t2 = t1.split('\n')
    # remove empty strings
    t3 = [x for x in t2 if x != '']
    d = {}
    # split at ":" and remove lines with not exactly one ":"
    # put entries into dictionary d
    for t in t3:
        spl = t.split(':')
        if (len(spl) == 2):
            entry = strip(spl[1])
            if (entry != ''):
                d[entry.lower()]=spl[0]
    return d

def backup(app):
    # parse robobackup-configuration.xml
    # check root element
    try:
        etree = parse("robobackup-configuration.xml")
    except:
        fatal(app,_("ERROR parsing robobackup-configuration.xml"))
    root = etree.getroot()
    if root.tag != "backup":
        fatal(app,_("robobackup-configuration.xml does not have <backup> as root-element"))

    # initialize logbook
    logbook = Log()
    logbook.append(_("Backup started"))
    
    # execute pre-backup commands
    for child in root.findall(".//pre//command"):
        command = strip(child.text)
        executeShellCommand(command,app)
    
    # query system for available devices
    deviceNames = getDeviceNames(app)
    
    # build destinations list
    # destination[0] = path
    # destination[1] = relative path for logfolder on the backupmedium
    # destination[2] = options for robocopy depending on the backupmedium
    destinations = []

    # parse backupmedia
    for child in root.findall(".//backupmedia//backupmedium"):

        # parse robocopy options depending on the backupmedium
        robocopyoptions = ""
        if child.find("robocopyoptions") != None:
            robocopyoptions = strip(child.find("robocopyoptions").text)

        # parse logfolder location on the backupmedium
        # standard logfolder is "log_robobackup"
        logfolder = "log_robobackup"
        if child.find("logfolder").text != None:
            logfolder = strip(child.find("logfolder").text)

        # parse data location
        path = ""
        external = child.find("mediumtype//external")
        absolute = child.find("mediumtype//absolute")
        
        if ((external == None) and (absolute == None)) or ((absolute != None) and (external != None)):
            fatal(app,_("Wrong configuration. Backupmedium//mediumtype//.. not specified correctly."))

        if absolute != None:
            # retrieve absolute path
            path = strip(absolute.text)

        if external != None:
            # retrieve drivename
            name = external.find("drivename")
            if name == None:
                fatal(app,_("Wrong configuration: drivename not specified correctly."))
            name = strip(name.text).lower()

            # retrieve relative path on drive
            pathondrive = external.find("pathondrive")
            if pathondrive == None:
                fatal(app,_("Wrong configuration: pathondrive not specified correctly."))
            pathondrive = strip(pathondrive.text)

            # search drive
            if name in deviceNames:
                path = deviceNames[name] + ":\\" + pathondrive
            else:
                logbook.append(_("Devicename ") + name + _(" not found: Did you forget to plug in your USB stick? Is a network folder missing?"))
                logbook.setLogOrange()

        # add a destination if the path is not empty ( = drive name not found )
        if path != "":
            destinations.append([path,logfolder,robocopyoptions])

    # retrieve general options for robobackup
    # retrieve errorlevel = minimum error to report
    errorlevel = root.find(".//minErrorToReport")
    if errorlevel != None:
        errorlevel = int(strip(errorlevel.text))
    else:
        errorlevel = 1
        logbook.append(_("minErrorToReport not specified in configuration. It is set to 1."))
                
    # iterate through destinations and items
    for destination in destinations:
        for child in root.findall(".//items//item"):
            # retrieve global robocopy options for all items
            # global options may be overriden by local options
            globaloptions = ""
            if root.find(".//globalrobocopyoptions//forall") != None:
                globaloptions = globaloptions + strip(root.find(".//globalrobocopyoptions//forall").text)
        
            # retrieve robocopyoptions for item
            robocopyoptions = ""
            if child.find("robocopyoptions") != None:
                robocopyoptions = strip(child.find("robocopyoptions").text)

            # retrieve whether an extra folder should be created
            # for every year, month, day
            dately = ""
            if child.find("dateoption//createYearlyFolder") != None:
                dately = "year" + str(date.today().year)
            if child.find("dateoption//createMonthlyFolder") != None:
                dately = "month" + str(date.today().year)
            if child.find("dateoption//createDailyFolder") != None:
                dately = str(date.today())

            # retrieve extra folder that should be created
            relative = ""
            if child.find("createFolder") != None:
                relative = strip(child.find("createFolder").text)

            # set full path of robocopy log directory
            logdir = destination[0] + "\\" + destination[1]
            try:
                if not os.path.exists(logdir):
                    os.makedirs(logdir)
            except:
                fatal(app,_("ERROR creating log folder: ") + logdir)
            log = "/LOG+:" + logdir + "\\log-" + str(date.today()) + ".txt"

            # create destination path
            dst = destination[0] + "\\" + dately + "\\" + relative
            try:
                if not os.path.exists(dst):
                    os.makedirs(dst)
            except:
                fatal(app,_("ERROR creating destination folder: ") + dst)

            # feth item path
            itemPath = child.find("path")
            if itemPath != None:
                itemPath = strip(itemPath.text)
            else:
                fatal(app,_("Wrong configuration: item did not contain a valid path"))

            execRobo = True
            # construct "source destination filespec" depending on whether the item is a directory or not
            robocommand = "robocopy "
            if isdir(itemPath):
                if root.find(".//globalrobocopyoptions//folder") != None:
                    globaloptions = globaloptions + " " + strip(root.find(".//globalrobocopyoptions//folder").text)
                robocommand = robocommand + itemPath + " " + dst + "\\" + itemPath.rsplit('\\',1)[1]
            elif isfile(itemPath):
                filename = itemPath.rsplit('\\',1)[1]
                filefolder = itemPath.rsplit('\\',1)[0]
                if root.find(".//globalrobocopyoptions//file") != None:
                    globaloptions = globaloptions + " " + strip(root.find(".//globalrobocopyoptions//file").text)
                robocommand = robocommand + filefolder + " " + dst + " " + filename
            else:
                # if the item is a regular file nor a folder it will not be copied
                # execRobo will be set to false
                logbook.append(_("Neither file nor folder: ") + itemPath + "\r\n" + _("The item was not copied."))
                logbook.setLogOrange()
                execRobo = False

            if execRobo:
                # add global robocopyoptions and execute robocopy
                robocommand = robocommand + " " + globaloptions + " " + robocopyoptions + " " + log
                executeRobocopy(robocommand,errorlevel,app)

    # execute post-backup commands
    for child in root.findall(".//post//command"):
        command = strip(child.text)
        executeShellCommand(command,app)

    # Backup successfull
    logbook.append(_("Robobackup ended successfully."))
    app.setBackupSuccess()
    if logbook.getLogOrange():
        app.setBackupCheck()
        logbook.append(_("Some copy orders have not been executed. Contact you administrator, if you don't know why."))
    app.setLog(logbook.getLog())

# install translation
translation = gettext.translation("robobackup", "locale", ["de"])
translation.install()
autostart = True
# execute the whole script
if len(sys.argv) == 2:
    if sys.argv[1] == "-nogui":
        autostart = False
BackupApp(ask = autostart).mainloop()
