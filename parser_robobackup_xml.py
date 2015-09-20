# -*- coding: utf-8 -*-

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
from defusedxml.ElementTree import parse
from subprocess import check_output, CalledProcessError, DEVNULL
from datetime import date
from collections import defaultdict
from logtools import logbook
import os

def strip(string):
    """
    Remove whitespaces at the front and the back of the given string.
    If the string is None, an empty String is returned.
    """
    if string != None:
        return string.rstrip().lstrip()
    else:
        return ""

def get_dict_drivename_to_letter():
    """
    Returns {<drivename1>: [<driveletter1>, ...], ...}
    The drivenames are lower case to get distinct dictionary keys.
    It may be that a drivename is associated with multiple letters.
    """
    wmiccmd = "wmic logicaldisk get caption, volumename"
    try:
        # universal_newlines=True ensures that \r\n is replaced by \n
        # in the output
        wmicresult = check_output(wmiccmd, shell=True, \
            universal_newlines=True, stderr=DEVNULL, stdin=DEVNULL)
    except CalledProcessError:
        logbook.critical(wmiccmd)
    # wmicresults is a table:
    # "Caption   VolumeName" \n\n
    # <driveletter>:   <drivename> \n\n
    # ...
    # wmicresult is split at "\n". A list is created.
    wmicresultlist = wmicresult.split("\n")
    # Empty strings "", which result from \n\n from list, are removed.
    wmicresultlist_cleaned = [x for x in wmicresultlist if x != ""]
    # The list looks like this:
    # ["Caption VolumeName", "<driveletter1>:   <drivename1>", ...]
    dict_drivename_to_letter = defaultdict(list)
    for wmicresultlist_entry in wmicresultlist_cleaned:
        # A split at ":" separates the wmicresultlist_entry in a list
        # with two parts [<driveletter>, <drivename>].
        list_letter_name = wmicresultlist_entry.split(":")
        # The caption of the table does not contain ":".
        # Do only continue, if there are two list entries in
        # list_letter_name.
        if len(list_letter_name) == 2:
            # A strip removes whitespaces from the drive name.
            name = strip(list_letter_name[1])
            # If a drive has no name, the string will be empty and
            # nothing will be done.
            if name != "":
                # Otherwise, the drive letter is stored in the
                # dict_drivename_to_letter.
                dict_drivename_to_letter[name.lower()].append(\
                    list_letter_name[0])
    return dict(dict_drivename_to_letter)

def get_driveletter(drivename):
    """
    Returns the corresponding drive letter to the drive name.
    If multiple drives have the same drive name, an exception will be
    thrown. You should rename the device.
    If the drive name is not found, a warning will be issued and None
    will be returned.
    """
    drivename = drivename.lower()
    device_names = get_dict_drivename_to_letter()
    try:
        driveletterlist = device_names[drivename]
        driveletterlist_length = len(driveletterlist)
    except KeyError:
        driveletterlist_length = 0
    if driveletterlist_length == 0:
        logbook.warning(_("Devicename ") + drivename + _(" not found"))
        return None
    elif driveletterlist_length > 1:
        logbook.critical(\
            _("Multiple devices with the same name found."))

    return driveletterlist[0]

def get_list(root, key):
    """
    Returns a list to the key. If no entries are found, an empty list
    [] will be returned.
    """
    return [strip(x.text) for x in root.findall(key)]

def parse_location(mediumtype, mediumtypekeyname="mediumtype"):
    """
    Returns the path to a data location. This location may be specified
    either as external device or absolute path. None will be returned,
    if the external device is missing.
    """
    external = mediumtype.find(mediumtypekeyname + "//external")
    internal = mediumtype.find(mediumtypekeyname + "//internal")

    # A data location must be gven as external device or internal path.
    if ((external == None) and (internal == None)) or \
        ((internal != None) and (external != None)):
        logbook.critical(mediumtypekeyname + \
            _(" not specified correctly."))

    # An internal path is just read.
    if internal != None:
        path = strip(internal.text)
        if path == "":
            logbook.critical(_("Empty absolute path."))
        if not os.path.isabs(path):
            path = os.path.join(\
                os.path.dirname(os.path.abspath(__file__)), path)

    # The drive letter is acquired by asking the OS for the drive name.
    # The full path is a concatenation of the drive letter and the
    # relative path on the drive.
    if external != None:
        name = get_content(external, "drivename", \
            logfunction=logbook.warning).lower()

        pathondrive = get_content(external, "pathondrive", \
            logfunction=logbook.info).lower()

        path = get_driveletter(name)
        if path != None:
            path += ":\\" + pathondrive

    return path

def get_content(root, key, logfunction, mustbedefined=False, \
    default_content_if_not_defined=""):
    """
    This function returns the text of the key element of root.
    If the key element has no text, the default content is set.
    The log message varies, depending on mustbedefined.
    A custom log function can be given.
    """
    result = root.find(key)
    if result == None:
        result = default_content_if_not_defined
        if mustbedefined:
            logfunction(key + _(" not present in configuration."))
        else:
            logfunction(key + _(" set to default value: ") + \
                result + ".")
    else:
        result = strip(result.text)
    return result

class Parser():
    """
    Parser reads the XML config file and does some checks.
    """
    def __init__(self):
        self._configuration_file_ = "robobackup-configuration.xml"
        # parse robobackup-configuration.xml
        # check root element
        try:
            path = os.path.join(os.path.dirname(\
                os.path.relpath(__file__)), \
                self._configuration_file_)
            etree = parse(path)
        except: # pylint: disable=bare-except
            logbook.critical(_("Error parsing ") + \
                self._configuration_file_)
        self._root_ = etree.getroot()
        if self._root_.tag != "backup":
            logbook.critical(self._configuration_file_ + \
                _(" does not have <backup> as root-element"))
    def parse(self, inlet):
        """
        Depending on what you want to parse, multiple inlets can be
        fed to Parser.
        """
        return inlet.execute(self._root_)

class PreCommandInlet():
    def execute(self, root):
        """
        Returns the list of commands to run before the backup.
        If the XML contains no commands, an empty list [] is returned.
        """
        return get_list(root, ".//pre//command")

class PostCommandInlet():
    def execute(self, root):
        """
        Returns the list of commands to run after the backup.
        If the XML contains no commands, an empty list [] is returned.
        """
        return get_list(root, ".//post//command")

class GlobalOptionsInlet():
    def execute(self, root):
        """
        Returns a dictionary which contains the global options
        like minimum errorlevel and global commandline options.
        Global commandline options may be overriden by local options
        (coming from backupmedia or items).
        """

        errorlevel = int(get_content(root, \
            ".//minErrorToReport", \
            default_content_if_not_defined="1", \
            logfunction=logbook.info))

        globaloptions = get_content(root, \
            ".//globalrobocopyoptions//forall", \
            logfunction=logbook.info)

        fileoptions = get_content(root, \
            ".//globalrobocopyoptions//file", \
            logfunction=logbook.info)

        folderoptions = get_content(root, \
            ".//globalrobocopyoptions//folder", \
            default_content_if_not_defined="/E", \
            logfunction=logbook.info)

        nrprocesses = int(get_content(root, \
            ".//nrProcesses", \
            default_content_if_not_defined="2", \
            logfunction=logbook.info))

        return {"errorlevel": errorlevel, \
            "globaloptions": globaloptions.split(), \
            "fileoptions": fileoptions.split(), \
            "folderoptions": folderoptions.split(), \
            "nrprocesses": nrprocesses}

class BackupmediaInlet():
    def execute(self, root):
        """
        Returns a list of all destinations. Each destination is
        represented as a dictionary.
          destination["path"] = path
          destination["relpathlogs"] = relative path for logs
          destination["robocopyoptions"] = options for robocopy
            depending on the backupmedium
        """
        destinations = []

        for child in root.findall(".//backupmedia//backupmedium"):

            robocopyoptions = get_content(child, "robocopyoptions", \
                logfunction=logbook.debug)

            # parse logfolder location on the backupmedium
            # standard logfolder is "logs"
            logfolder = get_content(child, "logfolder", \
                default_content_if_not_defined="logs", \
                logfunction=logbook.debug)

            # parse path and append the dictionary to destinations
            path = parse_location(child)
            if path != None:
                destinations.append({"path": path, \
                    "relpathlogs": logfolder, \
                    "robocopyoptions": robocopyoptions.split()})

        return destinations

class TruecryptInlet():
    def execute(self, root):
        """
        Returns a dictionary with two lists of Truecrypt commands.
        One list is for mounting crypto volumes, the other is for
        unmounting the same volumes.
        """
        truecryptmounts = []
        truecryptunmounts = []

        if root.find(".//truecrypt") != None:

            truecryptbinstring = get_content(root, \
                ".//truecrypt//truecryptbin", \
                mustbedefined=True, \
                logfunction=logbook.critical)

            for child in root.findall(".//truecrypt//mount"):

                # if external device is not available
                # continue, a warning is issued by parse_location
                pathtoimage = parse_location(child, \
                    mediumtypekeyname="imagetomount")
                if pathtoimage == None:
                    continue

                keyfile = None
                if child.find("key//file") != None:
                    keyfile = parse_location(child, \
                        mediumtypekeyname="key//file")
                    # although defined not available, decryption will
                    # fail, thus continue
                    if keyfile == "":
                        continue

                keyword = get_content(child, "key//word", \
                    logfunction=logbook.debug)

                # skip mount if there are not keys
                # a warning is issued
                if (keyfile == None) and (keyword == ""):
                    logbook.warning(_("Wrong configuration. Truecrypt key not specified correctly"))
                    continue

                # a password and a keyfile can occur simultaneously
                auth = []
                if keyfile != None:
                    auth.extend(["/k", keyfile])
                if keyword != "":
                    auth.extend(["/p", keyword])

                # letter specification for (un)mounting
                mount = []
                unmount = []
                letter = get_content(child, "letter", \
                    mustbedefined=True, \
                    logfunction=logbook.warning)
                if letter != "":
                    if len(letter) != 1:
                        logbook.warning(_("Wrong configuration. Letter where to mount the Truecrypt image has a length unequal one."))
                        continue
                    letter = letter[0:1]
                    mount = ["/l", letter]
                    unmount = ["/d", letter]
                else:
                    continue

                silent = ["/q", "/s"]

                truecryptmount = [truecryptbinstring]
                truecryptmount.extend(["/v", pathtoimage])
                truecryptmount.extend(auth)
                truecryptmount.extend(mount)
                truecryptmount.extend(silent)

                truecryptunmount = [truecryptbinstring]
                truecryptunmount.extend(unmount)
                truecryptunmount.extend(silent)

                truecryptmounts.append(truecryptmount)
                truecryptunmounts.append(truecryptunmount)

        return {"truecryptmounts": truecryptmounts, \
            "truecryptunmounts": truecryptunmounts}

class ItemInlet():
    def execute(self, root):
        """
        Returns a list of all items. Each item is stored
        as a dictionary.
          item["path"] = path to the item to backup
          item["relative"] = relative path to add on the backupmedium
          item["dately"] = relative path to add on the backupmedium
            depending on the date
          item["robocopyoptions"] = options for
            robocopy depending on the item
        """
        items = []

        for child in root.findall(".//items//item"):

            robocopyoptions = get_content(child, "robocopyoptions", \
                logfunction=logbook.debug)

            # retrieve whether an extra folder should be created
            # either each year or each month or each day
            dately = ""
            checkdately = 0
            if child.find("dateoption//createYearlyFolder") != None:
                dately = "year" + str(date.today().year)
                checkdately += 1
            if child.find("dateoption//createMonthlyFolder") != None:
                dately = "month" + str(date.today().month)
                checkdately += 1
            if child.find("dateoption//createDailyFolder") != None:
                dately = str(date.today())
                checkdately += 1

            if checkdately > 1:
                logbook.warning(_("Minor error in configuration: create???Folder."))

            relative = get_content(child, "createFolder", \
                logfunction=logbook.debug)

            item_path = get_content(child, "path", \
                mustbedefined=True, \
                logfunction=logbook.critical)

            items.append({"dately":dately, \
                "robocopyoptions":robocopyoptions.split(), \
                "relative":relative, \
                "path":item_path})

        return items
