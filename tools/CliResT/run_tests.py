# Copyright Javor
#
# Authors:
# - Javor
#
# Functionality:
# Highly configurable tests of Rucio upload and download
# THIS IS EXECUTABLE SCRIPT
# CONFIGURATION in common/vars.py

import logging
import os

from common.clients_tests import ClientUnitTests
from common.vars import LoggerConfig, TestConfig
from copy import copy
from datetime import date
from rucio.client import Client
from rucio.common.utils import adler32

rucio_client = Client()
logger_config = LoggerConfig()
test_config = TestConfig()

# general config
today = str(date.today())
logdir = logger_config.logdir
wrkdir = test_config.wrkdir

# rse expression determining set of rses to test 
exp = test_config.rse_expression

# file used in tests without registration
filename = test_config.test_file_no_register
filepath = test_config.filepath

# file used in tests with registration
filename_regi = test_config.test_file_register

# creation of the test file
t_file = open(filepath, 'w')
t_file.write('For test purposes only.')
t_file.close()

##### MAIN TEST LOOP ####
def run_test():

    _setup()

    for rse in _list_rses(exp):

        # rse and replica:
        unit_test = ClientUnitTests()
        rsename = rse['rse']
        unit_test.scope = 'user.ddmadmin'
        unit_test.lfn = filename
        unit_test.no_register = True
        unit_test.checksum, size = _file_stats(filepath)

        # logger related cfg:
        log_name = logdir +'/' + rsename + '.log'
        logging.basicConfig(filename=log_name, level=logging.DEBUG)
        logger = logging.getLogger()
        logger.info('Testing on %s against rse %s \n' % (today, rsename))
        unit_test.logger = logger 

        # chain of unit tests:
        logger.info('#U1########## UPLOAD test without registration, ################')
        upload_pfn(unit_test, rsename)
        logger.info('#U2########## UPLOAD test without registration, second attepmt: ################')
        upload_pfn(unit_test, rsename)
        logger.info('#U3########## UPLOAD test, with registration: ################')
        upload_register(unit_test, rsename)
        logger.info('#U4########## UPLOAD test, with registration, second attempt: ################') 
        upload_register(unit_test, rsename)
        logger.info('#D1########## DOWNLOAD with pfn: ###############')
        download_pfn(unit_test, rsename)
        logger.info('#D2######### DOWNLOAD with pfn, second attempt + update of the replica state: ###############')
        download_pfn(unit_test, rsename)
        register_and_update(rsename, unit_test.scope, unit_test.lfn, size, unit_test.checksum, logger)
        logger.info('#D3######### DOWNLOAD without pfn, src not defined: ###############')
        download_did(unit_test)
        logger.info('#D4######### DOWNLOAD without pfn, second attempt, src defined: ###############')
        download_did(unit_test, rsename=rsename)

        # logging clenup
        for handler in logging.root.handlers[:]:
             logging.root.removeHandler(handler)

##### UNIT TESTS #####
def upload_pfn(unit_test, rsename):
  
    t = copy(unit_test)
    t.rse = rsename
    t.src = filepath   
    try:
        t.copy_out_pfn()
    except Exception as e:
        t.logger.warning(str(e))
    t.logger.info('upload ended \n')


def upload_register(unit_test, rsename):

    t = copy(unit_test)
    t.rse = rsename
    t.src = filepath
    t.lfn = filename_regi
    t.no_register = False
    try:
        t.logger.info('no_register: %s' % t.no_register)
        t.copy_out()
    except Exception as e:
        t.logger.warning(str(e))
    try:
        state = rucio_client.get_did(t.scope, t.lfn)
        if state: 
            t.logger.info('Check registration: Registration successful')
    except Exception as e:
        t.logger.warning('Check registration: %s' % str(e))
    t.logger.info('upload ended \n')


def download_pfn(unit_test, rsename):

    t = copy(unit_test)
    t.rse = rsename
    t.dst = wrkdir + '/downloaded/'
    t.lfn = filename
    state = 'FAILED'
    try:
        state = t.copy_in_pfn()
    except Exception as e:
        t.logger.warning(str(e))
    d_pfn_state = os.path.exists(t.dst + filename)
    t.logger.info('Does downloaded file exist: %s' % d_pfn_state)
    t.logger.info('download ended \n')


def download_did(unit_test, rsename=None):

    t = copy(unit_test)
    t.pfn = None
    t.dst = wrkdir + '/downloaded/'
    t.lfn = filename_regi
    if rsename: t.rse = rsename
    try:
        t.copy_in()
    except Exception as e:
        t.logger.warning(str(e))
    d_did_state = os.path.exists(t.dst + filename_regi)
    t.logger.info('Does the downloaded file exist: %s' % d_did_state)
    t.logger.info('download ended \n')


####### SIDE METHODS ########
def _file_stats(filepath):

    a32 = adler32(filepath)
    size = int(os.path.getsize(filepath))

    return a32, size


def register_and_update(rsename, scope, name, size, checksum, logger):

    # register did
    try:
        rucio_client.add_did(scope, name, 'FILE')
    except Exception as e:
        logger.info('DID register %s' % str(e))

    # register replica
    try:
        rucio_client.add_replica(rsename, scope, name, size, checksum)
    except Exception as e:
        logger.info('REPLICA register %s' % str(e))

    # check replica state
    updating = 'Nothing happened.'
    try:
        updating = rucio_client.update_replicas_states(rsename, [{'scope':scope, 'name':name, 'state':'A'}])
    except Exception as e:
        updating = str(e)
    logger.info('Replicas state update attempt: %s\n' % updating)


def _list_rses(exp):
    rses = rucio_client.list_rses(exp)
    return rses


def _setup():

     if not os.path.exists(logdir):
         os.mkdir(logdir)


if __name__ == '__main__':
    run_test()
