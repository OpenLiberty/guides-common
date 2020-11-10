while getopts u:a:f: flag
do
    case "${flag}" in
        du) DOCKER_USERNAME=${OPTARG};;
        dp) DOCKER_PASSWORD=${OPTARG};;
        gt) GH_TOKEN=${OPTARG};;
    esac
done

git clone https://github.com/OpenLiberty/ci.docker.git
cd ci.docker/releases/latest/kernel-slim

GUIDES_TO_BUILD=(
    'guide-rest-intro'
    'guide-maven-intro'
    'guide-getting-started'
    'guide-microprofile-jwt'
    'guide-microprofile-opentracing'
    'guide-microprofile-config'
    'guide-kubernetes-intro'
    'guide-rest-client-java'
    'guide-microprofile-rest-client'
    'guide-microprofile-openapi'
    'guide-jpa-intro'
    'guide-microprofile-metrics'
    'guide-docker'
    'guide-rest-hateoas'
    'guide-maven-multimodules'
    'guide-cdi-intro'
    'guide-rest-client-angularjs'
    'guide-cloud-openshift'
    'guide-microprofile-health'
    'guide-gradle-intro'
    'guide-istio-intro'
    'guide-cors'
    'guide-spring-boot'
    'guide-arquillian-managed'
    'guide-kubernetes-microprofile-config'
    'guide-microprofile-fallback'
    'guide-sessions'
    'guide-bean-validation'
    'guide-security-intro'
    'guide-containerize'
    'guide-cloud-ibm'
    'guide-cloud-aws'
    'guide-microprofile-reactive-messaging'
    'guide-cloud-azure'
    'guide-rest-client-angular'
    'guide-microshed-testing'
    'guide-kubernetes-microprofile-health'
    'guide-microprofile-opentracing-jaeger'
    'guide-microprofile-reactive-messaging-acknowledgment'
    'guide-microprofile-istio-retry-fallback'
    'guide-microprofile-reactive-messaging-rest-integration'
    'guide-okd'
    'guide-rest-client-reactjs'
    'guide-cloud-google'
    'guide-reactive-rest-client'
    'guide-reactive-service-testing'
    'guide-social-media-login'
    'guide-cloud-openshift-operator'
    'guide-microprofile-rest-client-async'
    'iguide-circuit-breaker'
    'iguide-microprofile-config-intro'
    'iguide-bulkhead'
    'iguide-retry-timeout'
)

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