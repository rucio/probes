#!/bin/bash

curl 'https://raw.githubusercontent.com/rucio/rucio/master/tools/add_header' > add_header
python3 add_header $(find atlas/* -type f ) $(find cms/* -type f ) $(find common/* -type f -maxdepth 2)
