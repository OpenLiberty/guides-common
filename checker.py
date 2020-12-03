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
    pass


def adoc_checker(file):
    """
    Checks adoc file for style and license
    """
    checks = {
        "license": False,
        "release_date": False,

    }
    pass


def html_checker(file):
    """
    Checks html file for license
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
