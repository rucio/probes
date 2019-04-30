# Copyright Javor
#
# Authors:
# - Javor
#
# Functionality:
# Highly configurable tests of Rucio upload and download
# THIS IS A QUICK ANALYZER OF THE LOGS CREATED BY THE TEST
# - output in results.json
# CONFIGURATION in common/vars.py

import os
import sys
import json

from copy import copy, deepcopy
from common.vars import LoggerConfig, AnalStates
from datetime import date

rse = None
day = None
final_states = AnalStates()
results_table = 'results.json'

def run_analysis(rses):
    
    results = []
    for rse in rses.keys():
        try:
            result_rse = {'rse': rse}
            print 'analyzing rse: %s' % rse
            print day, rse, rses[rse]
            result = _analyze(rses[rse])
            result_rse['data'] = result
            results.append(result_rse)
        except Exception as e:
            print str(e)
            continue

    with open(results_table, 'w') as outfile:
         json.dump(results, outfile)

 
def _analyze(logpath):

    # current log of the test to be analyzed
    logfile = open(logpath, 'r')

    # custom variables form logs defined in common/vars.py
    log_config = LoggerConfig(day=day)
    test_ids = deepcopy(log_config.tests_order)
    test_id = test_ids[0]
    logger = log_config.logger_msgs
    tests = log_config.tests_defs

    # transforming log into dictionary
    for l in logfile.readlines():

        test_ident = '#%s#' % test_ids[0]
        ll = l.strip('\n').split(':')
        if len(ll) > 2:
            logger_level = ll[0]
            logger_location = ll[1]
            logger_msg = ll[2]
            for i in xrange(3, len(ll)):
                logger_msg = logger_msg + ':' + ll[i]
            if logger_level in logger.keys():
                tests[test_id][logger_level].append(logger_msg)
 
        if test_ident in l:
            test_id = test_ids[0]
            if len(test_ids) > 1:
                test_ids.pop(0)       

    # evaluate errors and warnings
    anal_result = deepcopy(final_states.results)
    for t in log_config.tests_order:
        
        counter_ok = [0, 0]
        for level in logger.keys():

            # if something goes really wrong
            if level == 'WARNING' or level == 'ERROR':
                for lm in tests[t][level]:
                     if lm not in log_config.accepted_warnings:
                         anal_result[t] = final_states.FAILED

            # evaluate if the result is what we expected
            if log_config.expected_output[t][level]:
                counter_ok[0] += 1
                if log_config.expected_output[t][level] in tests[t][level]:
                    counter_ok[1] +=1

        # if expected result occur, than OK, else SUSPICOUS
        if anal_result[t] == final_states.EMPTY:
            if counter_ok[0] == counter_ok[1]:
                anal_result[t] = final_states.OK
            else:
                anal_result[t] = final_states.SUSPICIOUS

    return anal_result


if __name__ == '__main__':

    try:
        rse = sys.argv[1]
    except:
        pass

    try:
        day = sys.argv[2]
    except:
        day = str(date.today())

    log_conf = LoggerConfig(day=day) 
    log_dir = log_conf.logdir
    
    log_exist = os.path.exists(log_dir)
    if not log_exist:
        print 'LOG directory not found'
        sys.exit()

    rses = {}
    if not rse or rse == 'ALL':
        for l in os.listdir(log_dir):
            if '.log' not in l:
                continue
            rse = l.split('DATADISK')[0]+'DATADISK'
            logpath = log_dir + '/' + l
            rses[rse] = logpath 
    else:
        logpath = log_dir + '/' + rse + '.log'
        rses[rse] = logpath

    run_analysis(rses)
