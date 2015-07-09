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
from subprocess import call
from os.path import isdir
from os.path import isfile
from datetime import date
import os
import multiprocessing as mp

from parser_robobackup_xml import Parser, PreCommandInlet, \
    PostCommandInlet, GlobalOptionsInlet, BackupmediaInlet, \
    ItemInlet, TruecryptInlet

def exec_shell_cmd(command):
    """
    Just a wrapper to call with option shell=True.
    """
    return call(command, shell=True)

def check_cmd_results(commands, results, logbook, minerror=1):
    """
    Works on two lists: commands and results. If the results (return
    codes) are bigger than minerror, it will be jotted down in the
    logbook and an exception will be raised.
    If the lists are empty, nothing happens.
    """
    failed_cmds = [x for (x, y) in zip(commands, results) \
        if y >= minerror]
    if failed_cmds != []:
        failed_cmds_and_error_code = [("cmd: " + x, "return code: " + \
            str(y)) for (x, y) in zip(commands, results) \
                if y >= minerror]
        logbook.critical(failed_cmds_and_error_code)

def exec_cmds_and_check(pool, cmds, logbook):
    """
    Executes cmds and checks results.
    """
    results = pool.map(exec_shell_cmd, cmds)
    check_cmd_results(cmds, results, logbook)

def create_folder(path, logbook):
    """
    Creates a folder in a given path. If an error occurs, it will be
    noted and and exception will be raised.
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except os.error:
        logbook.critical(_("Error creating folder: ") + path)

def backup(logbook):
    """
    Main function. It will do the backup. If it fails badly, an
    exception will be raised.
    """
    logbook.info(_("Backup is started."))

    # read options from the XML
    logbook.info(_("The configuration is read."))
    parser = Parser(logbook)
    options = parser.parse(GlobalOptionsInlet())
    truecrypt = parser.parse(TruecryptInlet())
    pre_commands = parser.parse(PreCommandInlet())
    post_commands = parser.parse(PostCommandInlet())
    destinations = parser.parse(BackupmediaInlet())
    items = parser.parse(ItemInlet())

    # create pool of processes
    pool = mp.Pool(processes=options["nrprocesses"]) # pylint: disable=no-member

    # mount crypto volumes
    exec_cmds_and_check(pool, truecrypt["truecryptmounts"], logbook)

    # execute commands before the backup
    exec_cmds_and_check(pool, pre_commands, logbook)

    # backup all items
    for item in items:

        # use multiple processes to backup the same item to
        # multiple destinations
        robocmdlist = []

        # path of the item under consideration
        itempath = item["path"]

        # store item in all destinations
        for dest in destinations:

            logdir = os.path.join(dest["path"], dest["relpathlogs"])
            logfile = os.path.join(logdir, "log" + str(date.today()) + \
                os.extsep + "txt")
            create_folder(logdir, logbook)

            destdir = os.path.join(dest["path"], item["relative"], \
                item["dately"])
            create_folder(destdir, logbook)

            execrobo = True
            # construct "source destination filespec"
            # - for directories:
            #   robocopy srcdir dstdir <options>
            # - for files:
            #   robocopy srcdir dstdir filename <options>
            robocommand = "robocopy "

            if isdir(itempath):
                # os.path.dirname(itempath) will return the wrong path
                # if the path specified in itempath does not end with
                # a backslash "\"
                robocommand += itempath + " " + destdir
                # add globaloptions for directories
                robocommand += " " + options["folderoptions"]
            elif isfile(itempath):
                robocommand += os.path.dirname(itempath) + " " + \
                    destdir + " "  + os.path.basename(itempath)
                # add globaloptions for files
                robocommand += " " + options["fileoptions"]
            else:
                logbook.warning(_("Neither file nor folder: ") + \
                    itempath + " " + _("The item was not copied."))
                execrobo = False

            if execrobo:
                # Add further options and append it to the list of
                # robocopy commands.
                # It seems to be that robocopy chooses the last
                # option, if two options contradict each other
                # so if [a] and [b] say different things:
                # robocopy <src> <dst> [file] [b] [a]
                # then [a] will probably be executed.
                # This has been tested for /e and /s.
                # /e means copy empty subfolders.
                # /s means exclude empty subfolders.
                # <options for files/folders>
                # <globaloptions>
                # <options from the backup medium>
                # <options from individual files>
                # In the ideal case the options are chosen such that
                # they do not overlap.
                # The author of this code does not take any warranty
                # that robocopy will always behave this way.
                robocommand += " " + options["globaloptions"] + " " + \
                    dest["robocopyoptions"] + " " + \
                    item["robocopyoptions"] + "/LOG+:" + logfile
                robocmdlist.append(robocommand)

        results_robocmdlist = pool.map(exec_shell_cmd, robocmdlist)
        check_cmd_results(robocmdlist, results_robocmdlist, logbook, \
            minerror=options["errorlevel"])

    # execute commandos after the backup
    exec_cmds_and_check(pool, post_commands, logbook)

    # unmount crypto volumes
    exec_cmds_and_check(pool, truecrypt["truecryptunmounts"], logbook)

    logbook.info(_("Backup is finished."))
    return
