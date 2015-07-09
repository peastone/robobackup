Robobackup
==========

Robobackup is a backup tool designed for Windows (R) operating system. 
It makes use of robocopy, a tool which is included with the operating 
system. 
Robobackup is not affiliated with the company behind the Windows (R)
operating system. 
Robobackup is free software and may be changed and used according to the
information given in the LICENSE file.

Sample configuration
--------------------
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
