#!/bin/python
# -*- coding: utf-8 -*-
"""
Traktor Librarian v0.9
A tool to clean up your Traktor library from duplicates.
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
        print("Removing duplicates..."),
        lib.remove_duplicates()
        print("DONE")

        lib.report()

        if not conf["test"]:
            lib.flush()
            print("\nTraktor library updated.")
        else:
            print("\nTest run. No changes made to the library.")

    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(1)


def get_traktor_dir():

    base_dir = os.path.expanduser("~")

    if sys.platform == "darwin":
        base_dir = os.path.join(base_dir, u"Documents")
    elif sys.platform == "win32":
        base_dir = os.path.join(base_dir, u"My Documents")
        
    traktor_dir = os.path.join(base_dir, u"Native Instruments", u"Traktor*")
    traktor_dir = glob(traktor_dir)

    if traktor_dir:
        # if the Traktor directory exists, then we get the last entry
        return traktor_dir[-1]

    return ""


def is_traktor_running():

    if sys.platform == "darwin":
        try:
            subprocess.check_output(['pgrep', 'Traktor'])
            return True
        except subprocess.CalledProcessError:
            return False
    elif sys.platform == "win32":
        output = subprocess.check_output(['tasklist', '/FI', "IMAGENAME eq Traktor.exe"]).decode("ascii", "ignore")
        if output.find("Traktor.exe") != -1:
            return True
        else:
            return False


def parse_arguments():
    # Parse arguments
    parser = argparse.ArgumentParser(description=("Traktor Librarian. Cleans up and fixes incostistencies in Traktor"
                                                  " library"))
    parser.add_argument('-l', '--library', help='Path to Traktor Library directory. If not provided the default location is used',
                        type=str)
    parser.add_argument('-t', '--test', help='Do a test run without making any changes to the library',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='Increase output verbosity', action='store_true')
    args = parser.parse_args()

    # Check that Traktor is not running. Quit if it does.
    if is_traktor_running():
        logger.error("Traktor is running. Please quit Traktor first.")
        return False

    if args.library:
        conf["library_dir"] = args.library
    else:
        conf["library_dir"] = get_traktor_dir()

    # check that collection.nml exists in the Traktor library directory
    collection_path = os.path.join(conf["library_dir"], u"collection.nml")

    if not os.path.exists(collection_path):
        logger.error(u"Traktor library not found: {}".format(collection_path))
        return False
    else:
        print("Using Traktor library found in {}\n".format(conf["library_dir"]))

    conf["test"] = args.test
    conf["verbose"] = args.verbose

    return True


if __name__ == '__main__':

    if parse_arguments():
        main()
    else:
        sys.exit(1)
