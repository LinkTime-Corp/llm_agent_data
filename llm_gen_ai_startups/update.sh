#!/bin/bash

set -e -u

CUR_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

ts=$(date +%Y%m%d)

set +u
if [ "" == "$eds_home" ]; then
    eds_home=$(realpath ~/llmeds)
fi
set -u

pushd . >/dev/null 2>&1 
cd "${CUR_PATH}"

git co main
git pull
git co -b data_"$ts"
git push --set-upstream origin data_"$ts"
cp "${eds_home}"/src/applications/startup_list/startup_list.latest.json startup_list.json
cp "${eds_home}"/src/applications/startup_list/startup_list.latest.csv startup_list.csv
python plot.py
git add .
git commit -m "update data $ts"
git push

popd >/dev/null 2>&1 
