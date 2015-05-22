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
from clean import Cleaner
from export import Exporter
from library import Library

logger = logging.getLogger(__name__)
sh = logging.StreamHandler()
sh.setLevel(logging.ERROR)
sh.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger.addHandler(sh)


def main():
    try:
        lib = Library(conf["library_dir"])

        if conf["action"] == "duplicates":
            cleaner = Cleaner(lib)
            print("Removing duplicates..."),
            cleaner.remove_duplicates()
            print("DONE")

            cleaner.report()

            if not conf["test"]:
                lib.flush()
                print("\nTraktor library updated.")
            else:
                print("\nTest run. No changes made to the library.")
        elif conf["action"] == "export":
            exporter = Exporter(lib, conf["export_dir"])
            exporter.export()


    except Exception as e:
        logger.error(e, exc_info=True)
        sys.exit(1)



def is_traktor_running():

    if sys.platform == "darwin":
        try:
            subprocess.check_output(['pgrep', 'Traktor'])
            return True
        except subprocess.CalledProcessError as e:
            return False
    elif sys.platform == "win32":
        output = subprocess.check_output(['tasklist', '/FI', "IMAGENAME eq Traktor.exe"]).decode("ascii", "ignore")
        if output.find("Traktor.exe") != -1:
            return True
        else:
            return False


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


def library_exists(directory):
    collection_path = os.path.join(directory, u"collection.nml")
    if not os.path.exists(collection_path):
        logger.error(u"Traktor library not found: {}".format(collection_path))
        return False
    else:
        return True



def parse_arguments():
    # Parse arguments
    parser = argparse.ArgumentParser(description=("Traktor Librarian. Cleans up and fixes incostistencies in Traktor"
                                                  " library"))

    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument('-d', '--duplicates', help='Clean Traktor Library from duplicates.',
                        action='store_true')
    source_group.add_argument('-e', '--export', help='Export the entire Traktor Library to a given location.',
                        type=str)

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

    if library_exists(conf["library_dir"]):
        print("Using Traktor library found in {}\n".format(conf["library_dir"]))
    else:
        logger.error(u"Traktor library not found in : {}".format(conf["library_dir"]))
        return False

    conf["test"] = args.test
    conf["verbose"] = args.verbose
    conf["filelog"] = True

    if args.duplicates:
        conf["action"] = "duplicates"
    elif args.export:
        conf["action"] = "export"
        conf["export_dir"] = args.export
    else:
        logger.error(u"Please specify an action")
        return False


    return True


if __name__ == '__main__':

    if parse_arguments():
        main()
    else:
        sys.exit(1)
