import json
import requests

BASE_REPO_URL = "https://api.github.com/orgs/OpenLiberty/repos"
JSON_PATH = ".github/workflows/drafts-to-test.json"
# Guides listed here require Java 17 or 21 and are tested in daily-build-java17.yml /
# daily-build-java21.yml instead. Keeping them here causes "invalid target release"
# compile failures when the Java 11 runner tries to build them.
DEPRECATED = [
    "guide-okd",
    # Java 17 guides (tested in guides-java17.json / daily-build-java17.yml)
    "guide-contract-testing",
    "guide-gradle-multimodules",
    "guide-jakarta-faces",
    "guide-jakarta-websocket",
    "guide-jms-intro",
    "guide-liberty-deep-dive",
    "guide-liberty-deep-dive-gradle",
    "guide-microprofile-telemetry-grafana-automatic",
    "guide-microprofile-telemetry-grafana-custom",
    "guide-jakarta-data",
    # Java 21 guides (tested in guides-java21.json / daily-build-java21.yml)
    "guide-jpa-intro",
    "guide-spring-boot",
]
HEADERS = {
    "Accept": "application/vnd.github.v3+json"
}

def published_guide_name(name):
    return "guide-" == name[:6]

if __name__ == "__main__":
    output = []

    r = requests.get(BASE_REPO_URL)

    if 'link' in r.headers:
        links = r.headers['link'].split(",")
        total_pages = int(links[1].split("page=")[1].split(">")[0])
    else:
        total_pages = 1

    for page in range(1, total_pages):
        r = requests.get(f'{BASE_REPO_URL}?sort=full_name&page={page}')
        for repo in r.json():
            repo_name = repo["name"]
            if published_guide_name(repo_name):
                if repo_name not in DEPRECATED:
                    output.append(repo_name)

    drafts = json.load(open(JSON_PATH))
    output += drafts

    print(output)
