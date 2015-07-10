Robobackup
==========

Robobackup is a backup tool designed for Windows (R) operating system. 
It makes use of robocopy, a tool which is included with the operating 
system. 
Robobackup is not affiliated with the company behind the Windows (R)
operating system. 
Robobackup is free software and may be changed and used according to the
information given in the LICENSE file.

Installation
------------

1. Install Python.
2. Install defusedxml for parsing the configuration file.
3. Install PyQt for the graphical user interface.
4. Install Truecrypt for encryption (optional, only if you use it).
5. Edit your configuration file (see next section). For that I recommend XML Notepad 2007

To install defusedxml, execute one of these commands:
```
pip install defusedxml (from internet)
pip install defusedxml-0.4.1.zip (this file in the current working directory)
```

Robobackup was developed with the following software in mind:

| Software | Version | Download link | SHA1 (64bit version) |
| ------------- |:-------------:| -------------|------------|
| Python        | 3.4.3 | https://www.python.org/downloads/release/python-343/      |SHA1(python-3.4.3.amd64.msi)= 8f2e4453dcdf424f15b14b2eda127e76fad4207f|
| defusedxml    | 0.4.1 | https://pypi.python.org/pypi/defusedxml| SHA1(defusedxml-0.4.1.zip)= d24866fadad6e5bd771757437af2c392f627c3ca|
| PyQt          | 5.4.2 | http://www.riverbankcomputing.com/software/pyqt/download5 |SHA1(PyQt5-5.4.2-gpl-Py3.4-Qt5.4.2-x64.exe)= 8ab016bc8b2f9d0c24370e52939bc51165c56927|
| Truecrypt     | 7.1a | http://www.heise.de/download/truecrypt.html               |SHA1(truecrypt_setup_7.1a.exe)= 7689d038c76bd1df695d295c026961e50e4a62ea|
| XML Notepad 2007 | 2.5 | http://www.heise.de/download/xml-notepad.html | SHA1(XmlNotepad.msi)= 31b728ddafaffaece76ceefe7d2be9e1a37c8a4b |

Sample configuration
--------------------
For editing the configuration, I like XML Notepad 2007:
http://www.heise.de/download/xml-notepad.html

A template can be found in robobackup-configuration.xml.

Assume, you want to backup the two folders "MyPictures" (on drive C) and "MyMovies" (on drive D)
and the folder "MyFamilyMovies" from a network drive (your FamilyComputer). This is how you do it:

```
<items>
  <item>
    <path>C:\MyPictures</path>
  </item>
  <item>
    <path>D:\MyMovies</path>
  </item>
  <item>
    <path>\\FamilyComputer\MyFamilyMovies</path>
  </item>
</items>
```

You also have to specify the place, where the files should be stored. Here we assume,
you want them to be stored on a USB stick with the name 'MyBackupDrive' under the folder
'backup'. Further, you want to store the backup on a network drive, which was mapped under Z.
You may notice, that additional options for robocopy may be added. If you want, you can
specify a log folder for every medium.

```
<backupmedia>
  <backupmedium>
    <mediumtype>
      <external>
        <drivename>MyBackupDrive</drivename>
        <pathondrive>backup</pathondrive>
      </external>
    </mediumtype>
    <logfolder>logs</logfolder>
  </backupmedium>
  <backupmedium>
    <logfolder>logs</logfolder>
    <mediumtype>
      <absolute>Z:\</absolute>
    </mediumtype>
    <robocopyoptions>/IPG:7</robocopyoptions>
  </backupmedium>
</backupmedia>
```

Robocopy options can be obtained by executing 

```
(>:) robocopy /?
```

in the shell (>:). 
Please look into the code for further explanation. You are welcome to write further examples for
this section.

Future developments
-------------------

Robobackup might
- support multiple configuration files
- give names to commands
- comment options in the XML
- optional backupmedia (no error, when missing)

Checklist for developers
------------------------

Please look at the following sources of errors:
- paths to external resources (You must know your working directory!)

Use the following tools:
- pyflakes: seems to be quick at spotting errors
- pylint: many false positives, but useful

It will be great, if you:
- translate as much as you can
- add docstrings to describe all relevant classes, methods and functions
- take care of appropriate error handling (if you spot something new, try to patch it)

Picture credit
--------------

Now all pictures for Robobackup have been created by myself. I release
them into public domain. You can easily adapt them.
