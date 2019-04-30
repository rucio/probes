#!/usr/bin/env python
import json
import os

from elasticsearch import Elasticsearch
from random import choice
from datetime import datetime
from copy import deepcopy
from hashlib import sha1

from ssl import create_default_context

# pem key to access ES
context = create_default_context(cafile="/etc/pki/tls/certs/CERN-bundle.pem")

# elastic config
es = Elasticsearch(
   ['es-atlas.cern.ch/es'],
   http_auth=('es-atlas', 'v~$&<J8/cG9]*eQ@'),
   scheme="https",
   port=443,
   ssl_context=context
)

# final state dict
state_dict = {'OK':0, 'SUSPICIOUS':1, 'FAILED':2}

# results of analysis of the tests
results_json = os.getcwd() + '/' + 'results.json'
with open(results_json) as f:
    results = json.load(f)

index = 'atlas_rucio-upload-download-tests-%s' % datetime.today().strftime("%Y.%m")

# dump it to ES
for rse_r in results:
    data = {}
    for t in rse_r['data'].keys():
          data[t] = state_dict[rse_r['data'][t]]
    rse = rse_r['rse']
    timestamp = str(datetime.utcnow().date())
    data['timestamp'] = timestamp
    data['rse'] = rse
    id = sha1(":".join((rse, timestamp))).hexdigest()
    res = es.index(index=index, doc_type='doc', id=id, body=data)
