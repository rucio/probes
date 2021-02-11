#!/usr/bin/env python
# Copyright European Organization for Nuclear Research (CERN) 2020
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Eric Vaandering, <ewv@fnal.gov>, 2020

import json

from rucio.common.config import config_get


def get_prometheus_config():
    prom_servers = config_get('monitor', 'prometheus_servers', raise_exception=False, default='')
    if prom_servers != '':
        prom_servers = prom_servers.split(',')
    prom_prefix = config_get('monitor', 'prometheus_prefix', raise_exception=False, default='')
    prom_label_config = config_get('monitor', 'prometheus_labels', raise_exception=False, default=None)
    if prom_label_config:
        try:
            prom_labels = json.loads(prom_label_config)
        except ValueError:
            prom_labels = None
    else:
        prom_labels = None
    return prom_servers, prom_prefix, prom_labels
