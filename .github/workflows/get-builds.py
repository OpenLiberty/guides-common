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
                info = requests.get(f'{BASE_DHE_URL}/{build}/info.json').json()
                if "driver_location" in info:
                    driver_location = info["driver_location"]
                    build_level = driver_location[driver_location.find("cl") : driver_location.find(".zip")]
                    build_info = {
                        "date": build, 
                        "driver_location": driver_location, 
                        "build_level": build_level
                    }
                    yesterdays_builds.append(build_info)
    
    print(yesterdays_builds)
