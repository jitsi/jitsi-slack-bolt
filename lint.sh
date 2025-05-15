#!/usr/bin/env bash

echo "## running black"
black . --diff --check
if [ $? -ne 0 ]; then
    echo "reformatting needed; run 'black .'"
    exit 1
fi

echo -e "\n\n## running flake8 - will not fail the build"
flake8

exit 0
