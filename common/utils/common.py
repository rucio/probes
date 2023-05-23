#!/usr/bin/env python
# Copyright European Organization for Nuclear Research (CERN) 2020
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Eric Vaandering, <ewv@fnal.gov>, 2022

import json
import sys
from typing import Tuple, Dict, List, Optional

from prometheus_client import push_to_gateway
from rucio.common.config import config_get
from rucio.core.monitor import MetricManager

probe_metrics = MetricManager(prefix='rucio.probes')

def get_prometheus_config() -> Tuple[List, str, Dict]:
    prom_servers = config_get('monitor', 'prometheus_servers', raise_exception=False, default='')
    if prom_servers != '':
        prom_servers = prom_servers.split(',')
    else:
        prom_servers = []
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


class PrometheusPusher:
    """
    A context manager to abstract the business of configuring and pushing to prometheus
    """

    def __init__(self, registry: object, job_name: Optional[str] = None):
        self.registry = registry
        if job_name:
            self.job_name = job_name
        else:
            self.job_name = sys.argv[0]
        self.servers, self.prefix, self.labels = get_prometheus_config()

    def __enter__(self) -> Dict:
        """
        Give the caller everything it might need (prefix is all it does need)
        :return:
        """
        config = {'servers': self.servers, 'prefix': self.prefix, 'labels': self.labels, 'job': self.job_name}
        return config

    def __exit__(self, exc_type, exc_value, exc_traceback):
        for server in self.servers:
            try:
                push_to_gateway(server.strip(), job=self.job_name, registry=self.registry, grouping_key=self.labels)
            except:
                continue
