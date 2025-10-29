import json

JSON_PATH = ".github/workflows/guides-java21.json"
DRAFT_JSON_PATH = ".github/workflows/drafts-to-test-java21.json"

if __name__ == "__main__":
    output = json.load(open(JSON_PATH))
    draft = json.load(open(DRAFT_JSON_PATH))
    output += draft
    print(output)
