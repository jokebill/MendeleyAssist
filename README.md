# Mendeley Assistant

## Introduction

If you use Mendeley to organize your references, yet you have some files that you donot want to upload to the Mendeley cloud, the link to local files for these references might break when you switch between computers.

This script solves such problem by creating a table in MendeleyPaths.sqlite database (locates under res folder) which stores the external file location you set for each computer/system/user you use, and automatically fix the links of corresponding references in Mendeley database, before the Mendeley software is executed.

## Usage
Use `kernel.py` or `gui.py` to start the application.

If a new computer/system/user is detected, you will be prompted to enter the path to your external files, the location of Mendeley database file, and the location of Mendeley program file. The next time, application will fix the link automatically and call Mendeley program after the fixing.

You could use

`kernel.py --reset`

or

`gui.py --reset`

to reset the record corresponding to the current computer/system/user in MendeleyPaths.sqlite, you will be prompted to enter external file path, location of Mendeley database and program file again.

\

There is another tool `fixadddate.py`, which is designed to fix the incorrect `Added Date` when you migrates your reference database from Biblioscape. When you do such migrating, the `Added Date` for the references you imported will all be set to the date/time you did the importing, while the real `Added Date` are inserted to the Notes for each reference. You could use `fixadddate.py` to fix this problem, which reads the first line for each reference notes, and use it as the `Added Date` for that record. Note that such fixing is limited to references in a folder specified by `Folder_Name` argument.

`fixadddate.py <path/to/database> <Folder_Name>`

