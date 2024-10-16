#!/bin/bash

set -e -u

ts=$(date +%Y%m%d)

if [ "" == "$eds_home" ]; then
    eds_home=$(realpath ~/llmeds)
fi

git co main
git pull
git co -b data_"$ts"
git push --set-upstream origin data_"$ts"
cp "${eds_home}"/src/applications/startup_list/startup_list.latest.json startup_list.json
cp "${eds_home}"src/applications/startup_list/startup_list.latest.csv startup_list.csv
python plot.py
git add .
git commit -m "update data $ts"
git push