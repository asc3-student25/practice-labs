"""Deprecated utilities.

Some functions here are still referenced from other modules pending a
migration. Verify call sites before removing anything.
"""

import yaml


def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)


def legacy_formatter(data):
    return str(data).upper()
