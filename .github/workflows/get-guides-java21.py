import json

JSON_PATH = ".github/workflows/guides-java21.json"

if __name__ == "__main__":
    print(json.load(open(JSON_PATH)))
