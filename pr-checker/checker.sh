#!/bin/sh
set -o pipefail

repo=$1
pr_number=$2
URL="https://api.github.com/repos/$repo/pulls/$pr_number/files"
UPDATED_FILES="$(curl -s -X GET -G $URL | jq -r '[ .[] | select(.status != "removed") | .filename ]' | tr -d '\n')"
ALL_FILES="$(curl -s -X GET -G $URL | jq -r '[ .[] |  .filename ]' | tr -d '\n')"
echo $UPDATED_FILES
if [ $(echo $ALL_FILES | jq 'length') = 1 ] && [ $(echo $ALL_FILES | jq '.[0]' | tr -d '"') = "README.adoc" ]; then
    echo "Test can be skipped because only README.adoc was updated"
    echo "::set-output name=canSkip::true"
else
    echo "Need to run test"
    echo "::set-output name=canSkip::false"
fi

python3 tools/pr-checker/checker.py --deny tools/pr-checker/deny_list.json --warn tools/pr-checker/warning_list.json --tags tools/guide_tags.json $(echo $UPDATED_FILES | jq '.[]' | tr -d '"')
