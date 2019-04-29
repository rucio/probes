# ALL CONFIG SHOULD BE HERE
import os

from copy import copy, deepcopy
from datetime import date

tests_order = ['U1', 'U2', 'U3', 'U4', 'D1', 'D2', 'D3', 'D4']
today = str(date.today())
wrkdir = os.getcwd() + '/processed/'
logdir = wrkdir + today + '/'

class TestConfig():

    def __init__(self, day=today):
 
        # general test settings
        self.wrkdir = copy(wrkdir)
        self.rse_expression = 'type=DATADISK' # 'datapolicynucleus=True&type=DATADISK'
        self.test_file_no_register = 'test_%s.txt' % day
        self.filepath = wrkdir + self.test_file_no_register
        self.test_file_register = 'test_%s_regi.txt' % day


class LoggerConfig():

    def __init__(self, day=str(today)):
        
        # log related variables
        self.logdir = wrkdir + day + '/'
        self.day = day
        self.tests_order = copy(tests_order)
        self.logger_msgs = {'DEBUG':[], 'ERROR':[], 'INFO':[], 'WARNING':[]}
        self.tests_defs = {}
        for t in self.tests_order:
            self.tests_defs[t] = deepcopy(self.logger_msgs)
        self.accepted_warnings = ['rucio still needs a bug fix of the summary in the uploadclient']
        self.expected_output = {}
        for t in self.tests_order:
            self.expected_output[t] = {'DEBUG':None, 'ERROR':None, 'INFO':None, 'WARNING':None}
        
        # expected results found in the log
        self.expected_output['U1']['INFO'] = 'Successfully uploaded file test_%s.txt' % day
        self.expected_output['U2']['INFO'] = 'File already exists on RSE. Skipping upload' 
        self.expected_output['U3']['INFO'] = 'Successfully uploaded file test_%s.txt' % day
        self.expected_output['U4']['INFO'] = 'File already exists on RSE. Skipping upload'
        self.expected_output['U4']['DEBUG'] = 'Skipping dataset registration'
        self.expected_output['D1']['INFO'] = 'Does downloaded file exist: True'
        self.expected_output['D2']['INFO'] = 'Does downloaded file exist: True'
        self.expected_output['D3']['INFO'] = 'Does the downloaded file exist: True'
        self.expected_output['D4']['INFO'] = 'Does the downloaded file exist: True'


class AnalStates():

    def __init__(self):
        self.OK = 'OK'
        self.SUSPICIOUS = 'SUSPICIOUS'
        self.FAILED = 'FAILED'
        self.EMPTY = 'NOT KNOWN'
        self.results = {}
        for t in tests_order:
            self.results[t] = self.EMPTY
