import requests

from datetime import date, timedelta

BASE_DHE_URL = "https://public.dhe.ibm.com/ibmdl/export/pub/software/openliberty/runtime/nightly/"

def yesterday():
    return date.today() - timedelta(days=1)

if __name__ == "__main__":
    date_to_get = yesterday().isoformat()
    builds = requests.get(f'{BASE_DHE_URL}/info.json').json()
    yesterdays_builds = []

    if "versions" in builds:
        for build in builds["versions"]:
            if date_to_get in build:
                yesterdays_builds.append(build)
    
    print(yesterdays_builds)
