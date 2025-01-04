import argparse
import sys
from datetime import date, datetime
from lxml import etree
import re
import json
import os

today = date.today()


def valid(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        return False
    return True


def adoc_checker(file, valid_tags, rules):
    """
    Checks adoc file for style and license
    """
    lines = []
    output = ''
    rules['line-length']['lines'] = lines
    license_re = re.compile(
        "[Cc]opyright[ ]*[(][Cc][)][ ]*([0-9]{4})([,][ ]*([0-9]{4})){0,1}[ ]*")

    release_date_re = re.compile(
        ":page-releasedate:[ ]*([0-9]{4}[-][0-9]{2}[-][0-9]{2})")
    tags_re = re.compile(r":page-tags: *\[(.*)\]")
    list_re = re.compile("^- ")
    file_tags_re = re.compile("^.*(hide_tags=).*(tags=).*$")
    hotspot_re = re.compile(r"\[(hotspot(=[^ =\n]+)? ?)+( file(=[0-9]+)?)?\]`[^`\n]*`")

    skip_list = os.environ.get('SKIP_LIST')
    print(f"SKIP_LIST={skip_list}\n");
    
    for line_num, line in enumerate(file):
        if len(line) > 120:
            lines.append(line_num + 1)
        # checks '- ' and suggest to switch to '* '
        if rules['-']['check']:
            if not skip_list:
                list_match = list_re.match(line)
                if list_match != None:
                    output += f"[{rules['-']['log-level']}] [LINE {line_num + 1}] Use '* ' to enumerate items instead of '- '.\n"
        if rules['license']['check']:
            result = license_re.search(line)
            if result:
                years = result.groups()
                if years[-1] != None:
                    if years[-1] != str(today.year):
                        output += f"[{rules['license']['log-level']}] [LINE {line_num + 1}] Update the license to the current year.\n"
                    if years[0] >= years[-1]:
                        output += f"[{rules['license']['log-level']}] [LINE {line_num + 1}] Invalid years in license\n"
                else:
                    if years[0] != str(today.year):
                        output += f"[{rules['license']['log-level']}] [LINE {line_num + 1}] Update the license to the current year.\n"
                rules['license']['check'] = False
                rules['license']['found'] = True
        if rules['release_date']['check']:
            result = release_date_re.search(line)
            if result:
                date = result.groups()
                if not valid(date[-1]):
                    output += f"[{rules['release_date']['log-level']}] [LINE {line_num + 1}] Release date is invalid: {date[0]} + 1\n"
                    output += f"[{rules['release_date']['log-level']}] [LINE {line_num + 1}] The date should be in the form YYYY-MM-DD\n"
                rules['release_date']['check'] = False
                rules['release_date']['found'] = True
        if rules['page_tags']['check']:
            result = tags_re.search(line)
            if result:
                tags = result.groups()
                invalid_tags = []
                if len(tags) != 0:
                    tags = list(str(tags[0]).split(','))
                    for tag in tags:
                        if tag.strip(" '\"") not in valid_tags:
                            invalid_tags.append(tag)
                            output += f"[{rules['page_tags']['log-level']}] [LINE {line_num + 1}] {tag} is an invalid tag\n"
                    if len(invalid_tags) > 0:
                        output += f"[{rules['page_tags']['log-level']}] [LINE {line_num +1}] List of valid tags: {valid_tags}\n"
                        output += f"[{rules['page_tags']['log-level']}] [LINE {line_num +1}] Note that these tags are case sensitve\n"
                rules['page_tags']['check'] = False
        if rules['file_tags']['check']:
            result = file_tags_re.search(line)
            if result:
                output += f"[{rules['file_tags']['log-level']}] [LINE {line_num +1}] Define 'tags' in front of 'hide_tags'\n"
        if rules['hotspots']['check']:
            result = hotspot_re.findall(line)
            hotspots = line.count("[hotspot")
            if len(result) != hotspots:
                output += f"[{rules['hotspots']['log-level']}] [LINE {line_num +1}] Improperly formatted hotspot on this line\n"
                output += f"[{rules['hotspots']['log-level']}] [LINE {line_num +1}] Note that a hotspot should not be split between lines\n"


    if not rules['license']['found']:
        output += f"[{rules['license']['log-level']}] Add a license with the current year.\n"
    if not rules['release_date']['found']:
        output += f"[{rules['release_date']['log-level']}] Add a release date.\n"
    if rules['line-length']['lines']:
        output += f"[{rules['line-length']['log-level']}] The following lines are longer than 120 characters:\n"
        output += f"[{rules['line-length']['log-level']}] {rules['line-length']['lines']}\n"
        output += f"[{rules['line-length']['log-level']}] Consider wrapping text to improve readability.\n"
    return output


def check_vocabulary(file, deny_list, warning_list):
    """
    """
    file.seek(0)
    deny_occurrence, warning_occurrence = {}, {}
    deny = re.compile('|'.join(deny_list), re.IGNORECASE)
    warn = re.compile('|'.join(warning_list), re.IGNORECASE)
    output = ''
    for line_num, line in enumerate(file):
        if ':common-includes:' not in line:
            matched_deny = deny.findall(line)
            matched_warning = warn.findall(line)
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


def pom_xml_checker(file, guide_id, rules):
    """
    Checks if the artifactId in pom.xml starts with the guide's ID
    """
    guide_id = "guide-" + guide_id[len("guide-"):]
    output = ''

    path_parts = file.split(os.sep)  # Split the path by directory separator

    # Check if it's a direct pom.xml in the root of finish/start
    if path_parts[-2] in rules['main_directory']:
        # Base module (finish/pom.xml or start/pom.xml)
        expected_artifact_id = guide_id
    elif path_parts[-3] in rules['main_directory']:
        # module (finish/xxx/pom.xml or start/xxx/pom.xml)
        module_name = path_parts[-2]
        expected_artifact_id = f"{guide_id}-{module_name}"
    else:
        output += f"[ERROR] Unrecognized path structure for {file}.\n"
        return output

    try:
        tree = etree.parse(file)
        root = tree.getroot()
        namespace = root.nsmap.get(None)
        namespaces = {'m': namespace} if namespace else {}
        artifact_id_element = root.find('m:artifactId', namespaces=namespaces)
        if artifact_id_element is None or artifact_id_element.text is None:
            output += f"[ERROR] Project's artifactId not found.\n"
            return output

        artifact_id = artifact_id_element.text.strip()
        line_number = artifact_id_element.sourceline
        if artifact_id != expected_artifact_id:
            output += f"[ERROR] [LINE {line_number}] The project's artifactId '{artifact_id}' does not match the expected '{expected_artifact_id}'.\n"

    except:
        e = sys.exc_info()[0]
        print(f"something went wrong with {file} parsing", e)

    return output


def find_corresponding_pom_xml(server_file):
    """
    Given a server.xml path, finds the corresponding pom.xml path.
    """    
    path_parts = server_file.split(os.sep)

    try:
        src_index = path_parts.index('src')
    except ValueError:
        # 'src' not found in path; cannot determine pom.xml location
        return None

    module_root_dir = os.sep.join(path_parts[:src_index])
    pom_xml_path = os.path.join(module_root_dir, 'pom.xml')
    if os.path.exists(pom_xml_path):
        return pom_xml_path
    else:
        return None
    

def extract_artifact_id(pom_file):
    """
    Extracts the artifactId from the given pom.xml file.
    """
    try:
        tree = etree.parse(pom_file)
        root = tree.getroot()
        namespace = root.nsmap.get(None)
        namespaces = {'m': namespace} if namespace else {}

        artifact_id_element = root.find('m:artifactId', namespaces=namespaces)
        if artifact_id_element is not None and artifact_id_element.text:
            return artifact_id_element.text.strip()
    except:
        e = sys.exc_info()[0]
        print(f"something went wrong with {pom_file} parsing", e)

    return None


def server_xml_checker(file):
    """
    Checks if the location attribute in server.xml's webApplication element
    matches the artifactId from pom.xml.
    """
    output = ''

    try:
        tree = etree.parse(file)
        root = tree.getroot()

        # Find the webApplication element
        web_app_element = root.find(".//webApplication")
        if web_app_element is None:
            output += f"[ERROR] webApplication element not found.\n"
            return output

        # Get the location attribute
        location = web_app_element.get("location")
        if location is None:
            line_number = web_app_element.sourceline
            output += f"[ERROR] [LINE {line_number}] location attribute not found in the webApplication element.\n"
            return output

        pom_file = find_corresponding_pom_xml(file)
        artifact_id = extract_artifact_id(pom_file)
        # Expected location is the artifactId with .war extension
        expected_location = f"{artifact_id}.war"

        if location != expected_location:
            line_number = web_app_element.sourceline
            output += f"[ERROR] [LINE {line_number}] webApplication location '{location}' does not match the expected '{expected_location}'.\n"
    except:
        e = sys.exc_info()[0]
        print(f"something went wrong with {file} parsing", e)

    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--deny', nargs=1,
                        type=argparse.FileType('r'))
    parser.add_argument('--warn', nargs=1,
                        type=argparse.FileType('r'))
    parser.add_argument('--tags', nargs=1,
                        type=argparse.FileType('r'))
    parser.add_argument('--adoc-rules', nargs=1,
                        type=argparse.FileType('r'))
    parser.add_argument('--xml-rules', nargs=1,
                        type=argparse.FileType('r'))
    parser.add_argument('--repo', nargs=1, type=str)
    parser.add_argument('infile', nargs='*',
                        type=argparse.FileType('r'), default=sys.stdin)
    args = parser.parse_args()

    if args.deny is not None:
        try:
            deny_list = json.loads(args.deny[0].read())
        except:
            e = sys.exc_info()[0]
            print("something went wrong with deny list parsing", e)
            deny_list = []
    if args.warn is not None:
        try:
            warning_list = json.loads(args.warn[0].read())
        except:
            e = sys.exc_info()[0]
            print("something went wrong with warning list parsing", e)
            warning_list = []
    if args.tags is not None:
        try:
            tags = list(filter(lambda tag: 'visible' in tag and tag['visible'] == 'true', json.loads(
                args.tags[0].read())['guide_tags']))
            tags = list(map(lambda tag: tag['name'], tags))
        except:
            e = sys.exc_info()[0]
            print("something went wrong with tags parsing", e)
            tags = []
    if args.adoc_rules is not None and args.repo is not None:
        try:
            repo = args.repo[0].split('/')[-1]
            adoc_rules = dict(map(lambda adoc_rules: (adoc_rules[0], {'check': repo not in adoc_rules[1]['exception'], 'log-level': adoc_rules[1]['log-level']}),
                             json.loads(args.adoc_rules[0].read()).items()))
        except:
            e = sys.exc_info()[0]
            print("something went wrong with repo and adoc-rules parsing", e)
            adoc_rules = {
                "license": {'check': True, 'log-level': 'ERROR'},
                "release_date": {'check': True, 'log-level': 'ERROR'},
                "page_tags": {'check': True, 'log-level': 'ERROR'},
                "-": {'check': True, 'log-level': 'ERROR'},
                "line-length": {'check': True, 'log-level': 'WARNING'},
                "file_tags": {'check': True, 'log-level': 'ERROR'},
            }
    if args.xml_rules is not None and args.repo is not None:
        try:
            repo = args.repo[0].split('/')[-1]
            xml_rules = {"check": repo not in (xml_data := json.loads(args.xml_rules[0].read()))['skip'], 'main_directory': xml_data['main_directory']}
        except:
            e = sys.exc_info()[0]
            print("something went wrong with repo and xml-rules parsing", e)
            xml_rules = { "check" : False }

    file_extensions = map(lambda f: f.name.split(
        '/')[-1].split('.')[-1], args.infile)
    output = ''

    for i, f in enumerate(file_extensions):
        if f == 'adoc':
            result = adoc_checker(args.infile[i], tags, adoc_rules) + check_vocabulary(args.infile[i], deny_list, warning_list)
            if result != '':
                output += f"[INFO] File:[{args.infile[i].name}]\n{result}"

    for i, file in enumerate(args.infile):
        if os.path.basename(file.name) == 'pom.xml' and xml_rules["check"]:
            result = pom_xml_checker(file.name, repo, xml_rules)
            if result:
                output += f"[INFO] File:[{file.name}]\n{result}"

        if os.path.basename(file.name) == 'server.xml' and xml_rules["check"]:
            path_parts = file.name.split(os.sep)
            if path_parts[-2] == 'staging' or path_parts[-3] == 'staging':
                continue
            pom_xml_path = find_corresponding_pom_xml(file.name)
            pom_xml_result = pom_xml_checker(pom_xml_path, repo, xml_rules)
            if pom_xml_result:
                output += f"[INFO] File:[{pom_xml_path}]\n{pom_xml_result}"
                continue
            server_xml_result = server_xml_checker(file.name)
            if server_xml_result:
                output += f"[INFO] File:[{file.name}]\n{server_xml_result}"

    if output != '':
        print(output.rstrip())
        if 'ERROR' in output:
            sys.exit(1)
        else:
            sys.exit(0)
    else:
        sys.exit(0)
