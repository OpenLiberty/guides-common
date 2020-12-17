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
    output = ''

    license_re = re.compile(
        "[Cc]opyright[ ]*[(][Cc][)][ ]*([0-9]{4})([,][ ]*([0-9]{4})){0,1}[ ]*")
    for line_num, line in enumerate(file):
        if len(line) > 88:
            lines.append(line_num + 1)
        if checks["license"]:
            result = license_re.search(line)
            if result:
                years = result.groups()
                if years[-1] != None:
                    if years[-1] != today.year:
                        checks["license_message"] += f"[ERROR] [LINE {line_num + 1}] Update the license to the current year.\n"
                    if int(years[0]) >= int(years[-1]):
                        checks["license_message"] += f"[ERROR] [LINE {line_num + 1}] Invalid years in license\n"
                else:
                    if years[0] != today.year:
                        checks["license_message"] += f"[ERROR] [LINE {line_num + 1}] Update the license to the current year.\n"
                checks["license"] = False

    if checks['license']:
        output += f"[ERROR] Add a license with the current year.\n"
    if checks['license_message']:
        output += f"{checks['license_message']}"
    if checks["line_too_long"]:
        output += f"[ERROR] The following lines are longer than 88 characters:\n"
        output += f"{checks['line_too_long']}\n"
    return output


def adoc_checker(file):
    """
    Checks adoc file for style and license
    """
    lines = []
    output = ''
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
                if years[-1] != None:
                    if years[-1] != today.year:
                        output += f"[ERROR] [LINE {line_num + 1}] Update the license to the current year.\n"
                    if years[0] >= years[-1]:
                        output += f"[ERROR] [LINE {line_num + 1}] Invalid years in license\n"
                else:
                    if years[0] != today.year:
                        output += f"[ERROR] [LINE {line_num + 1}] Update the license to the current year.\n"
                checks["license"] = False
        if checks["release_date"]:
            result = release_date_re.search(line)
            if result:
                date = result.groups()
                if not valid(date[-1]):
                    output += f"[ERROR] [LINE {line_num + 1}] Release date is invalid: {date[0]} + 1\n"
                    output += f"[ERROR] [LINE {line_num + 1}] The date should be in the form YYYY-MM-DD\n"

    if checks['license']:
        output += '[ERROR] Add a license with the current year.\n'
    if checks['release_date']:
        output += '[ERROR] Add a release date.\n'
    if checks["lines"]:
        output += "[WARNING] The following lines are longer than 120 characters:\n"
        output += f"[WARNING] {checks['lines']}\n"
        output += "[WARNING] Consider wrapping text to improve readability.\n"
    return output


def html_checker(file):
    """
    Checks html file for license
    """
    output = ''
    license_re = re.compile(
        "[Cc]opyright[ ]*[(][Cc][)][ ]*([0-9]{4})([,][ ]*([0-9]{4})){0,1}[ ]*")
    checks = {
        "license": True,
    }
    for line_num, line in enumerate(file):
        if checks['license']:
            result = license_re.search(line)
            if result:
                years = result.groups()
                if years[-1] != None:
                    if years[-1] != today.year:
                        output += f"[ERROR] [LINE {line_num + 1}] Update the license to the current year.\n"
                    if years[0] >= years[-1]:
                        output += f"[ERROR] [LINE {line_num + 1}] Invalid years in license\n"
                else:
                    if years[0] != today.year:
                        output += f"[ERROR] [LINE {line_num + 1}] Update the license to the current year.\n"
                checks["license"] = False
                break
    return output


def check_vocabulary(file, deny_list, warning_list):
    """
    """
    file.seek(0)
    deny_occurrence, warning_occurrence = {}, {}
    deny = re.compile('|'.join(map(re.escape, deny_list)))
    warn = re.compile('|'.join(map(re.escape, warning_list)))
    output = ''
    for line_num, line in enumerate(file):
        line = re.sub('[^0-9a-zA-Z]+', ' ', line).split()
        matched_deny = list(filter(lambda word: deny.fullmatch(word), line))
        matched_warning = list(filter(lambda word: warn.fullmatch(word), line))
        if matched_deny:
            deny_occurrence[line_num] = matched_deny
        if matched_warning:
            warning_occurrence[line_num] = matched_warning
    if deny_occurrence:
        output += '[ERROR] The following words must be changed.\n'
        for line in deny_occurrence.keys():
            output += f'[ERROR] [LINE {line + 1}] {deny_occurrence[line]}\n'
    if warning_occurrence:
        output += '[WARNING] The following words should ideally be changed.\n'
        for line in warning_occurrence.keys():
            output += f'[WARNING] [LINE {line + 1}] {warning_occurrence[line]}\n'
    return output


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
        try:
            deny_list = json.loads(args.deny[0].read())
        except:
            deny_list = []
    if args.warn is not None:
        try:
            warning_list = json.loads(args.warn[0].read())
        except:
            Warning_list = []

    for file in args.infile:
        file_extension = file.name.split('/')[-1].split('.')[-1]
        output = ''
        if file_extension == 'adoc':
            output += adoc_checker(file)
        elif file_extension == 'java':
            output += java_checker(file)
        elif file_extension == 'html':
            output += html_checker(file)
        else:
            print("No checker yet.")
            sys.exit(0)

        output += check_vocabulary(file, deny_list, warning_list)

        if output != '' and 'ERROR' in output:
            print(output.rstrip())
            sys.exit(1)
        else:
            sys.exit(0)
