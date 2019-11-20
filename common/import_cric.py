#!/usr/bin/env python
#
# Copyright European Organization for Nuclear Research (CERN)

# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#                       http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Hannes Hansen, <hannes.jakob.hansen@cern.ch>, 2019
#
# Import CRIC data into rucio
#
# PY3K COMPATIBLE

import requests
import sys

from rucio.common.exception import RucioException
from rucio.core.importer import import_data

CRIC_URL = 'http://doma-cric.cern.ch/api/doma/rse/query/list/?json'

if __name__ == '__main__':
    rses = requests.get(CRIC_URL).json()
    data = {'rses': rses}
    try:
        import_data(data)
        sys.exit(0)
    except RucioException as e:
        print(e)
        sys.exit(2)
