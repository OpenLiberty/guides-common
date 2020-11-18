import requests

BASE_REPO_URL = "https://api.github.com/orgs/OpenLiberty/repos"

HEADERS = {
    "Accept": "application/vnd.github.v3+json"
}

def published_guide_name(name):
    return "guide-" in name and "draft" not in name and "archived" not in name

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
                output.append(repo_name)

    print(output)
