"""Deprecated utilities.

``load_config`` is still referenced from ``main`` pending a migration;
that is the reason this file survived the restructure. Remove unused
functions only after confirming no callers remain.
"""

import yaml


def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)


def legacy_formatter(data):
    return str(data).upper()
