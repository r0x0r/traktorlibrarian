# TraktorLibrarian 
Version 0.95

A command line tool for cleaning up duplicates in Traktor Library. Compatible with Mac OSX and Windows.

# Description
TraktorLibrarian is a small utility to help you keep your Traktor library nice and tidy. I wrote this tool, since Traktor does not have an option to remove duplicates from its library. It provides the following functionality:

* Removes duplicates from your Traktor library
* Smart choice of which duplicates are kept. Files with user set cue points are preferred over files with no user changes.
* Updates playlists with correct paths
* Test mode. In test mode it does not make any changes to the library, but just logs the changes it would make

TraktorLibrarian outputs its actions to the report.log file. You can browse the file to see what changes were made.

# Installation

If you have git installed, then type the following command in the command prompt

`git clone https://github.com/r0x0r/traktorlibrarian.git´

Or alternatively download a zip from here and unpack it to a directory of your choice

# Usage

If you are looking for a quick action, just type 

`python librarian.py`

This will remove duplicates from the library. The following options are supported

- `-l [path]` / `--library [path]` Path to Traktor Library directory. If not provided the default location of ~/Documents/Native Instruments/Traktor <latest version>  is used 
- `-t` / `--test` Do a test run without making any changes to the library
- `-v` / `--verbose` Print log information to the screen 


# FAQ

## TraktorLibrarian screwed up my library / messed up my playlists / killed my first-born etc.

Do not worry. TraktorLibrarian creates a backup of your library before making any changes. To restore a backup, look under *Traktor data directory/Backup/Librarian* for the latest backup, copy it to the Traktor data directory and rename it to *collection.nml*

## Where is the Traktor data directory?

On OSX the default location is *~/Documents/Native Instruments/Traktor*
On Windows it is *%USERPROFILE%/My Documents/Native Instruments/Traktor*

## How can I see what changes were made by TraktorLibrarian?

Look in the *report.log* file (located in the same directory as TraktorLibrarian) for all the changes that were made to the library.


# Changelog

## 0.95

- `New` Windows support
- `New` Python 3 support
- `Improved` More informative messages of what has been done
- `Improved` It can detect and handle correctly more than two duplicates
- `Fixed` Incorrect paths in playlists

## 0.9
 - First version

