# Rucio Probes

This repository hosts a collection of Nagios-style monitoring probes for [Rucio](https://rucio.cern.ch/). The probes are written in Python and organized into per-community directories — `atlas` and `cms` for experiment-specific checks, `common` for probes shared across multiple communities, and `attic` for unmaintained legacy code — covering health and consistency checks for Rucio servers, daemons, RSEs, and related infrastructure. Contributions are governed by community component leads, with stricter review rules for shared probes in `common` (requiring approval from leads of at least two communities) to protect the operations teams that depend on them.

Responsible for PR merging in [rucio/probes](https://github.com/rucio/probes): [Dimitrios Christidis](https://github.com/dchristidis), [Eric Vaandering](https://github.com/ericvaandering)
