while getopts u:a:f: flag
do
    case "${flag}" in
        -du) DOCKER_USERNAME=${OPTARG};;
        -dp) DOCKER_PASSWORD=${OPTARG};;
        -gt) GH_TOKEN=${OPTARG};;
    esac
done

GUIDES_TO_BUILD=(
    $(python3 .github/workflows/get-repos.py)
)

echo "Building following guides"
for guide in $GUIDES_TO_BUILD;
do
  echo $guide
done

git clone https://github.com/OpenLiberty/ci.docker.git
cd ci.docker/releases/latest/kernel-slim

echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin

yesterday=$(date -d "yesterday 13:00" '+%Y-%m-%d')
devBuildSize=$(curl $DHE_NIGHTLY_URL/info.json | jq '.versions | length')

echo "Building nightly builds from $yesterday"

for ((i=0; i < $devBuildSize; i++)); do
    currentDevBuild=$(curl $DHE_NIGHTLY_URL/info.json --silent | jq '.versions | .['$i']' | sed "s/\"//g")
    if [[ "$currentDevBuild" == *"$yesterday"* ]]; then
    # If build is from yesterday, build Docker image for it and run tests
    currentDevDriver=$(curl $DHE_NIGHTLY_URL/$currentDevBuild/info.json | jq '.driver_location'  | sed "s/\"//g")
    echo "Building from $currentDevDriver"
    
    DEVDATE=$currentDevBuild
    BUILDLEVEL="cl$(echo $currentDevDriver | awk -F '.zip' '{print $1}' | awk -F 'cl' '{print $2}')"
    
    sed -i '/&& wget/c\&& wget http://public.dhe.ibm.com/ibmdl/export/pub/software/openliberty/runtime/nightly/'$DEVDATE'/'$currentDevDriver' -U UA-Open-Liberty-Docker -O /tmp/wlp.zip \\' Dockerfile.ubuntu.adoptopenjdk8
    sed -i '/&& sha1sum/d' Dockerfile.ubuntu.adoptopenjdk8
    cat Dockerfile.ubuntu.adoptopenjdk8
    echo "Building $BUILDLEVEL from $DEVDATE"
    docker build -q -t $DOCKER_USERNAME/olguides:$BUILDLEVEL -f Dockerfile.ubuntu.adoptopenjdk8 .
    docker push $DOCKER_USERNAME/olguides:$BUILDLEVEL
    
    # Trigger daily builds for this OL build
    for GUIDE in "${GUIDES_TO_BUILD[@]}"; do
        curl -X POST -q \
            -H "Accept: application/vnd.github.v3+json" \
            -H "Authorization: token $GH_TOKEN" \
            https://api.github.com/repos/OpenLiberty/$GUIDE/dispatches \
            -d "{\"event_type\":\"daily-build\", \"client_payload\": { \"dev-date\": \"$DEVDATE\", \"dev-build\": \"$currentDevDriver\" }}"
    done
    fi
done
