# Contributing Guide

Thank you for participating in the probes development.
Please consider also consulting the [Rucio Contributing Guide](https://rucio.cern.ch/documentation/contributing/).
However, note that there are some deviations from it.

## How this repository is structured

The probes are organised in the following directories:

- `attic`: probes that are not being used by any community and, as such, are unmaintained and unsupported
- `common`: probes that are being actively used by more than one community
- community directories: probes that are used exclusively by one community

## How can a community participate

Please contact the [Rucio project leader](https://rucio.cern.ch/documentation/component_leads).
You will be asked to nominate one member of your community to join the existing component leads.
A new directory and a new label will be added.

## How to report an issue

Reporting bugs or requesting new features can be done by [opening an issue](https://github.com/rucio/probes/issues/new).
It is helpful to put the appropriate labels and, when known in advance, assign the person to work on them.

## How to submit a pull request

- Opening an issue beforehand is not required.
  However, it is recommended to do so when the change is expected to be sizeable.
- Fork the repository and create a new branch.
  It is helpful to name it appropriately.
- The subject of each commit must be prefixed by a label.
  This can be omitted for rare changes across the entire repository.
  If there is an issue related to the commit, then its number should be appended.
  For example, a commit may resemble this: `ATLAS: Port probes to Python 3 #1234`
- Once done, you may proceed with [opening a pull request](https://github.com/rucio/probes/compare).
  Choose the appropriate label that matches your commits.

## How to merge a pull request

A pull request affecting a community directory should be reviewed by one or more members of that community.
Then, the merge must be done by the appropriate component lead.
Same applies for moving probes into or out of the `attic` directory.

The `common` directory requires additional caution and care.
Each pull request affecting it must be formally approved by at least two leads from different communities.
Once done, finalising the merge is reserved for the component lead from ATLAS.

## Motivation

The development of probes in a common repository is considered most beneficial.
It can avoid duplicate effort but also inspire ideas and solutions across communities.

However, the probes greatly differ from the main Rucio repository.
For one thing, their implementation and usage can be significantly community-specific.
For another, they lack unit testing, documentation, long-term branches, and release notes.

The existence of dedicated community directories alleviates the first concern.
It offers flexibility in the acceptance of community-specific development guidelines and review procedures.
The stricter rules for the `common` directory should reduce the impact of the second concern.
There, the objective is to avoid introducing issues that would perturb the operations teams of other communities.
