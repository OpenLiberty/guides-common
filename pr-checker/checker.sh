repo=$1
pr_number=$2
URL="https://api.github.com/repos/$repo/pulls/$pr_number/files"
FILES=$(curl -s -X GET -G $URL | jq -r '[ .[] |  .filename ]' | tr -d '\n')

if [ $(echo $FILES | jq 'length') = 1 ] && [ $(echo $FILES | jq '.[0]' | tr -d '"') = "README.adoc" ]; then
    echo "Test can be skipped because only README.adoc was updated"
    echo "::set-output name=canSkip::true"
else
    echo "Need to run test"
    echo "::set-output name=canSkip::false"
fi

python3 pr-checker/checker.py --deny pr-checker/deny_list.json --warn pr-checker/warning_list.json $(echo $FILES | jq '.[]' | tr -d '"')
