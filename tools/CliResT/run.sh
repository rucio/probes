#!/bin/bash
RESULTS='./processed/'
SUMARIES='./processed/summaries/'
DATA='./processed/downloaded/'

if [ ! -d "$RESULTS" ]; then
    mkdir $RESULTS
fi

if [ ! -d "$SUMARIES" ]; then
    mkdir $SUMARIES
fi

if [ ! -d "$DATA" ]; then
    mkdir $DATA
fi

python run_tests.py
python quick_log_analyzer.py
python dump_to_es.py
