#! /bin/bash

cd /opt/monitor
rm -f ./log/*

find . -name "*~" -print0 | xargs -0 -r rm
find . -name "*.pyc" -print0 | xargs -0 -r rm
find . -name "*.7z" -print0 | xargs -0 -r rm
find . -name "__pycache__" -print0 | xargs -0 -r rm -rf

rm -rf ./bkup.*

rm -rf ./install/* > /dev/null 2>&1
rm Leonardo* > /dev/null 2>&1

