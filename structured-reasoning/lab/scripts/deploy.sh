#!/usr/bin/env bash
set -euo pipefail
echo "Deploying messy_project..."
PYTHONPATH=src python -m messy_project.main
