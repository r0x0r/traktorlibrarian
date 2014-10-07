#!/bin/python
# -*- coding: utf-8 -*-
"""
Traktor Librarian v0.9
A tool to clean up your Traktor library from duplicates and relocated missing files.
Works currently on Mac OSX only.
"""


import argparse
import os
import sys
import subprocess
import logging
from glob import glob

from conf import *
from traktorlibrary import Library

logger = logging.getLogger(__name__)
sh = logging.StreamHandler()
sh.setLevel(logging.ERROR)
sh.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(sh)


def main():
    try:
        lib = Library()

        if conf["fix_missing"]:
            print("Fixing missing files..."),
            lib.fix_missing_files()
            print("DONE")
        elif conf["remove_missing"]:
            print("Removing missing files..."),
            lib.fix_missing_files()
            print("DONE")

        if conf["remove_duplicates"]:
            print("Removing duplicates..."),
            lib.remove_duplicates()
            print("DONE")

        lib.process_playlists()
        lib.report()

        if not conf["test"]:
            lib.flush()
            print("\nTraktor library updated.")
        else:
            print("\nTest run. No changes made to the library.")

    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description=("Traktor Librarian. Cleans up and fixes incostistencies in Traktor"
                                                  " library"))
    parser.add_argument('-l', '--library', help='Path to Traktor Library directory. If not provided the default location is used',
                        type=str)
    parser.add_argument('-d', '--remove-duplicates', help="Delete duplicate files from the library",
                        action='store_true')
    parser.add_argument('-f', '--fix-missing', help="Attempt to locate missing files", action='store_true')
    parser.add_argument('-r', '--remove-missing', help="Remove missing files from the library", action='store_true')
    parser.add_argument('-a', '--all',
                        help="Perform all the tasks, ie attempt to locate missing files, remove duplicates and finally"
                             " remove files that could not be found. Same as the options -d -f -r combined.",
                        action='store_true')
    parser.add_argument('-t', '--test', help='Do a test run without making any changes to the library',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='Increase output verbosity', action='store_true')
    args = parser.parse_args()

    error = False

    # Check that Traktor is not running. Quit if it does.
    try:
        subprocess.check_output(['pgrep', 'Traktor'])
        logger.error("Traktor is running. Please quit Traktor first.")
        sys.exit(1)
    except subprocess.CalledProcessError:
        pass

    if args.library:
        conf["library_dir"] = args.library
    else:
        home_dir = os.path.expanduser("~")
        traktor_dir = os.path.join(home_dir, u"Documents", u"Native Instruments", u"Traktor*")
        traktor_dir = glob(traktor_dir)

        if traktor_dir:
            # if the Traktor directory exists, then we get the last entry
            conf["library_dir"] = traktor_dir[-1]

    # check that collection.nml exists in the Traktor library directory
    collection_path = os.path.join(conf["library_dir"], u"collection.nml")

    if not os.path.exists(collection_path):
        logger.error(u"Traktor library not found: {}".format(collection_path))
        sys.exit(1)
    else:
        print("Using Traktor library found in {}\n".format(conf["library_dir"]))

    if args.all:
        conf["fix_missing"] = True
        conf["remove_duplicates"] = True
        conf["remove_missing"] = True
    else:
        conf["fix_missing"] = args.fix_missing
        conf["remove_duplicates"] = args.remove_duplicates
        conf["remove_missing"] = args.remove_missing

    conf["test"] = args.test
    conf["verbose"] = args.verbose

    main()
