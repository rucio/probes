from commands import getstatusoutput
from os.path import dirname
import os
from copy import deepcopy

class FileSpec(object):

    _infile_keys =  ['lfn', 'ddmendpoint', 'type',
                    'dataset', 'scope',
                    'dispatchDblock', 'dispatchDBlockToken',
                    'guid', 'filesize', 'checksum',
                    'prodDBlock', 'prodDBlockToken',
                    'allowRemoteInputs', 'accessmode',
                    'cmtconfig' # Needed for Singularity
                    ]


    _outfile_keys = ['lfn', 'pfn', 'ddmendpoint', 'type',
                    'dataset', 'scope', 'checksum'
                    'destinationDblock', 'destinationDBlockToken',
                    'fileDestinationSE',
                    'dispatchDBlockTokenForOut',
                    'prodDBlockTokenForOutput', # exposed only for eventservice related job
                    'ddmendpoint_alt', # alternative location of ddmendpoint
                    'cmtconfig' # Needed for Singularity
                    ]

    _os_keys = ['eventRangeId', 'storageId', 'eventService', 'allowAllInputRSEs', 'pandaProxySecretKey', 'jobId', 'osPrivateKey', 'osPublicKey', 'pathConvention', 'taskId']

    _local_keys = ['type', 'status', 'replicas', 'surl', 'turl', 'mtime', 'status_code']

    def __init__(self, **kwargs):

        attributes = self._infile_keys + self._outfile_keys + self._local_keys + self._os_keys
        for k in attributes:
            setattr(self, k, kwargs.get(k, getattr(self, k, None)))

        self.filesize = int(getattr(self, 'filesize', 0) or 0)
        if self.eventService is None:
            self.eventService = False
        self.allowAllInputRSEs = False
        self.replicas = []

    def calculate_pfn(self, rse, scope, lfn):

        from rucio.client.rseclient import RSEClient
        c = RSEClient()
        did = scope + ':' + lfn
        pfn =''
        try:
           pfn = c.lfns2pfns(rse, [did])[did]
        except Exception as e:
           return str(e)
        return pfn

    def is_directaccess(self, *args, **kwargs):
        return False


class ClientUnitTests():

    def __init__(self):

        self.rse = None
        self.rse_settings = None
        self.lfn = None
        self.scope = None
        self.checksum = None
        self.src = None
        self.pfn = None
        self.wrkdir = None
        self.data = None
        self.corrupted_data = None
        self.fake_data = None       
        self.logger = None
        self.no_register = True
        self.turl = None
        self.summary_file_path = None
        self.tracing_rucio = False
        self.dst = None

    def filespec(self): 
        #test_file.write('For test purposes only.')
        fspec_ok = FileSpec()
        fspec_ok.lfn = self.lfn
        fspec_ok.scope = self.scope
        attrs = vars(self)
        #self.logger.info('Init. %s' % str(attrs))
        fspec_ok.checksum = self.checksum or None
        fspec_ok.pfn = self.src
        fspec_ok.ddmendpoint = self.rse
        fspec_ok.workdir = self.wrkdir or os.getcwd() + '/processed/'
        fspec_ok.turl = self.turl       
        fspec_ok.no_register = self.no_register

        self.data = fspec_ok
        rsename = self.rse or 'all-sites'
        self.summary_file_path = os.getcwd() + '/processed/summaries/summary_' + rsename + '.json'

        fspec_corrupted = deepcopy(fspec_ok)
        fspec_corrupted.checksum = '99999999' 
        self.corrupted_data = fspec_corrupted

        fspec_fake = deepcopy(fspec_ok)
        fspec_fake.lfn = 'test_buggy_name.txt'      
        self.fake_data = fspec_fake
 
    def copy_in(self):
        self.filespec()
        self.logger.info('Processing copy_in.')
        trace_report = {}
        trace_report.update(eventType='unit test')
        self.logger.info('file data: %s' % str(self.data))
        state = self._stage_in_api(self.dst, self.data, trace_report=trace_report)
        return state

    def copy_in_pfn(self):
        self.filespec()
        self.logger.info('Processing copy_in_dark. ')
        trace_report = {}
        trace_report.update(eventType='unit test')
        self.logger.info('file data: %s' % str(self.data.lfn))
        if not self.pfn:
            self.pfn = self.data.calculate_pfn(self.rse, self.scope, self.lfn)
        self.data.turl = self.pfn
        self.logger.info('pfn calculated: %s' % str(self.pfn))
        self.logger.info('download dst: %s' % str(self.dst))
        state = self._stage_in_api(self.dst, self.data, trace_report=trace_report)
        return state

    def copy_out(self):
        self.filespec()
        self.logger.info('Processing copy_out')
        trace_report = {}
        trace_report.update(eventType='unit test')
        self.logger.info('file data lfn: %s' % str(self.data.lfn))
        self.logger.info('no register: %s' % str(self.data.no_register))
        state = self._stage_out_api(self.data, self.summary_file_path, trace_report=trace_report)
        return state

    def copy_out_pfn(self):
        self.filespec()
        self.logger.info('Processing copy_out_pfn')
        trace_report = {}
        trace_report.update(eventType='unit test')
        self.logger.info('no register: %s' % str(self.data.no_register))
        if not self.pfn:
            self.pfn = self.data.calculate_pfn(self.rse, self.scope, self.lfn)
            self.data.turl = self.pfn
            self.logger.info('pfn calculated: %s' % str(self.pfn))
        state = self._stage_out_api(self.data, self.summary_file_path, trace_report=trace_report)
        return state

    def _stage_in_api(self, dst, fspec, trace_report=None):

        # init. download client
        from rucio.client.downloadclient import DownloadClient
        download_client = DownloadClient(logger=self.logger)

        # traces are switched off
        if hasattr(download_client, 'tracing'):
            download_client.tracing = self.tracing_rucio

        # file specifications before the actual download
        f = {}
        f['did_scope'] = fspec.scope
        f['did_name'] = fspec.lfn
        f['did'] = '%s:%s' % (fspec.scope, fspec.lfn)
        f['rse'] = fspec.ddmendpoint
        f['base_dir'] = dirname(dst)
        f['no_subdir'] = True
        if fspec.turl:
            f['pfn'] = fspec.turl

        if fspec.filesize:
            f['transfer_timeout'] = self.get_timeout(fspec.filesize)

        # proceed with the download
        self.logger.info('_stage_in_api file: %s' % str(f))
        trace_pattern = {}
        if trace_report:
            trace_pattern = trace_report
        result = []
        if fspec.turl:
            self.logger.info('_stage_in_api: processing with pfn download')
            result = download_client.download_pfns([f], 1, trace_custom_fields=trace_pattern)
        else:
            result = download_client.download_dids([f], trace_custom_fields=trace_pattern)

        client_state = 'FAILED'
        if result:
            client_state = result[0].get('clientState', 'FAILED')

        return client_state

    def _stage_out_api(self, fspec, summary_file_path, trace_report=None):

        # init. download client
        from rucio.client.uploadclient import UploadClient
        upload_client = UploadClient(logger=self.logger)

        # traces are turned off
        if hasattr(upload_client, 'tracing'):
	    upload_client.tracing = self.tracing_rucio
        if self.tracing_rucio:
	    upload_client.trace = trace_report

        # file specifications before the upload
        f = {}
        f['path'] = fspec.pfn if fspec.pfn else fspec.lfn
        f['rse'] = fspec.ddmendpoint
        f['did_scope'] = fspec.scope
        f['did_name'] = fspec.lfn
        f['no_register'] = fspec.no_register
        
        if fspec.filesize:
            f['transfer_timeout'] = get_timeout(fspec.filesize)

        if fspec.lfn and '.root' in fspec.lfn:
            f['guid'] = fspec.guid

        # process with the upload
        self.logger.info('_stage_out_api: %s' % str(f))
        result = None
        try:
	    result = upload_client.upload([f], summary_file_path)
        except UnboundLocalError:
	    self.logger.warning('rucio still needs a bug fix of the summary in the uploadclient')
	    result = 0

        client_state = 'FAILED'
        if result == 0:
	    client_state = 'DONE'

        return client_state

