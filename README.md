# TraktorLibrarian 
Version 0.9
A command line tool for cleaning up duplicates and relocating missing files in Traktor Library. Currently works on Mac OSX only

# Description
TraktorLibrarian is a small utility to help you keep your Traktor library nice and tidy. It provides the following functionality:

* Removes duplicates from your Traktor library
* Tries to relocate missing files 
* Removes missing files
* Test mode. In test mode it does not make any changes to the library, but just outputs the changes it would make

TraktorLibrarian outputs its actions to the report.log file. You can browse the file to see what changes were made.

Relocation of missing files is performed using OSX Spotlight search. In order it to work, you must have your music files in the Spotlight database. 

# Installation

If you have git installed, then type the following command in the command prompt

`git clone https://github.com/r0x0r/traktorlibrarian´

Or alternatively download a zip from here and unpack it to a directory of your choice

# Usage

If you are looking for a quick action, just type 

`python librarian.py --all´

This will remove duplicates from the library, relocates missing files and removes the missing files that cannot be located.

The more advanced use

`python librarian.py [options]´

The following options are supported

- `-l [path]` / `--library [path]` Path to Traktor Library directory. If not provided the default location of ~/Documents/Native Instruments/Traktor <latest version>  is used 
- `-d` / `--remove-duplicates` Delete duplicate files from the library
- `-f` / `--fix-missing` Attempt to locate missing files
- `-r` / `--remove-missing` Remove missing files
- `-a` / `--all` Perform all the tasks, ie attempt to locate missing files, remove duplicates and finally remove files that could not be found. Same as the options -d -f -r combined.
- `-t` / `--test` Do a test run without making any changes to the library
- `-v` / `--verbose` Print log information to the screen 


# FAQ

## TraktorLibrarian screwed up my library / messed up my playlists / killed my first-born etc.

Do not worry. TraktorLibrarian creates a backup of your library before making any changes. To restore a backup, look under <Traktor data directory>/Backup/Librarian for the latest backup, copy it to the Traktor data directory and rename it to *collection.nml*

## Where is the Traktor data directory?

On OSX it is located by default at ~/Documents/Native Instruments/Traktor <ver> 

## How can I see what changes were made by TraktorLibrarian?

Look in the *report.log* file (located in the same directory as TraktorLibrarian) for all the changes that were made to the library.




