import argparse
import sys
from datetime import date, datetime
import re
import json

today = date.today()


def valid(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        return False
    return True


def java_checker(file):
    """
    Checks java file for style and license
    """
    lines = []
    checks = {
        "license": True,
        "license_message": "",
        "line_too_long": lines,
    }

    license_re = re.compile(
        "[Cc]opyright[ ]*[(][Cc][)][ ]*([0-9]{4})([,][ ]*([0-9]{4})){0,1}[ ]*")
    for line_num, line in enumerate(file):
        if len(line) > 88:
            lines.append(line_num + 1)
        if checks["license"]:
            result = license_re.search(line)
            if result:
                years = result.groups()
                if years[-1] != today.year:
                    checks["license_message"] += "Update the license to the current year.\n"
                if len(years) > 1 and years[0] >= years[-1]:
                    checks["license_message"] += "Invalid years in license\n"
                checks["license"] = False
    print(checks["license_message"])
    if checks["line_too_long"]:
        print("The following lines are longer than 88 characters:")
        print(checks["line_too_long"])
    pass


def adoc_checker(file):
    """
    Checks adoc file for style and license
    """
    lines = []
    output = ""
    checks = {
        "license": True,
        "release_date": True,
        "lines": lines
    }
    license_re = re.compile(
        "[Cc]opyright[ ]*[(][Cc][)][ ]*([0-9]{4})([,][ ]*([0-9]{4})){0,1}[ ]*")
    release_date_re = re.compile(
        ":page-releasedate:[ ]*([0-9]{4}[-][0-9]{2}[-][0-9]{2})")

    for line_num, line in enumerate(file):
        if len(line) > 120:
            lines.append(line_num + 1)
        if checks["license"]:
            result = license_re.search(line)
            if result:
                years = result.groups()
                if years[-1] != today.year:
                    output += "Update the license to the current year.\n"
                if len(years) > 1 and years[0] >= years[-1]:
                    output += "Invalid years in license\n"
                checks["license"] = False
        if checks["release_date"]:
            result = release_date_re.search(line)
            if result:
                date = result.groups()
                if not valid(date[-1]):
                    output += f"Release date is invalid: {date[0]} at line {line_num + 1}\n"
                    output += "The date should be in the form YYYY-MM-DD\n"

    print(output)
    if checks["lines"]:
        print("The following lines are longer than 120 characters:")
        print(checks["lines"])
        print("Consider wrapping text to improve readability.")
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

        if file_extension == 'adoc':
            adoc_checker(file)

        elif file_extension == 'java':
            java_checker(file)

        elif file_extension == 'html':
            html_checker(file)

        else:
            print('its something else')
