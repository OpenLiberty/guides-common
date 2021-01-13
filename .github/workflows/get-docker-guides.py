import json

JSON_PATH = ".github/workflows/docker-guides.json"

if __name__ == "__main__":
    print(json.load(open(JSON_PATH)))
