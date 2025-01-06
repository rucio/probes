#!/usr/bin/env python
# Copyright European Organization for Nuclear Research (CERN) since 2012
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
from typing import Dict, List, Optional, Tuple

from rucio.common.config import config_get
from rucio.core.monitor import MetricManager

PROBES_PREFIX = 'rucio.probes'
probe_metrics = MetricManager(prefix=PROBES_PREFIX)


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

    def __init__(self, prefix: "Optional[str]" = PROBES_PREFIX, job_name: "Optional[str]" = None):
        self.job_name = job_name
        self.servers, _dummy, self.labels = get_prometheus_config()
        self.prefix = prefix

        self.manager = MetricManager(prefix=self.prefix, push_gateways=self.servers)

    def __enter__(self) -> "MetricManager":
        """
        Return the Rucio metrics manager
        :return:
        """
        return self.manager

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.manager.push_metrics_to_gw(job=self.job_name, grouping_key=self.labels)
