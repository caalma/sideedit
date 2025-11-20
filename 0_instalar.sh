#!/bin/bash

set -e

python -m venv pyvenv

. pyvenv/bin/activate

pip install -r app/requirements.txt
