import argparse
import sys
import datetime
import re
import json


def java_checker(file):
    """
    Checks java file for style and license
    """
    line = []
    checks = {
        "license": False,
        "line_too_long": line,
    }
    # // Copyright (c) 2018, 2009 IBM Corporation and others.
    license_re = re.compile(
        "[/]{2}[ ]*[Cc]opyright[ ]*[(][Cc][)][ ]*([,]{0,1}[ ]*[0-9]{4}){1,2}[ ]*IBM Coporation and others.")
    pass


def adoc_checker(file):
    """
    Checks adoc file for style and license
    """
    checks = {
        "license": False,
        "release_date": False,

    }
    release_date_re = re.compile(
        ":page-releasedate:[ ]*([0-9]{4}[-][0-9]{2}[-][0-9]{2})")
    pass


def html_checker(file):
    """
    Checks html file for license
    """
    pass


def check_vocabulary(file, deny_list, warning_list):
    """
    """
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--deny', nargs=1,
                        type=argparse.FileType('r'))
    parser.add_argument('--warn', nargs=1,
                        type=argparse.FileType('r'))
    parser.add_argument('infile', nargs='*',
                        type=argparse.FileType('r'), default=sys.stdin)
    args = parser.parse_args()

    if args.deny is not None:
        deny_list = json.loads(args.deny[0].read())
        deny = re.compile('|'.join(map(re.escape, deny_list)))
    if args.warn is not None:
        warning_list = json.loads(args.warn[0].read())
        warn = re.compile('|'.join(map(re.escape, warning_list)))

    for file in args.infile:
        file_extension = file.name.split('/')[-1].split('.')[-1]
        if file_extension is 'adoc':
            adoc_checker(file)

        elif file_extension is 'java':
            java_checker(file)

        elif file_extension is 'html':
            html_checker(file)

        else:
            print('its something else')
