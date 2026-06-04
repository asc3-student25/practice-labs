"""Deployment helpers.

Distinct from ``src/messy_project/helpers.py``. These functions are only
used by the shell scripts in this directory.
"""


def format_deploy_log(step, status):
    return f"[{step}] {status}"


def mark_release(version):
    return f"release-{version}"
