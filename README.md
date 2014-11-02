robobackup
==========

robobackup is a backup tool designed for Windows (R). It makes use of robocopy, a tool which
is included in the system. robobackup is not affiliated with Microsoft (R) or Windows (R). 
It is free software and may be changed and used according to the LICENSE.

sample configuration
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
Please look into the code for further explanation. You are welcome to write further examples for
this section.

picture credit
--------------
All pictures are public domain. You can easily take your own pictures.

police badge (SUCCESS.png): https://openclipart.org/detail/190442/gold-police-badge-by-jhnri4-190442

backup (BACKUP.png): https://openclipart.org/detail/104995/-by-rost

check engine (CHECK.png): https://openclipart.org/detail/193925/check-engine-by-j_iglar-193925

sos (FAIL.png): https://openclipart.org/detail/185926/sos-by-arvin61r58-185926
