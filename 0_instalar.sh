#!/bin/bash

set -e

python3.9 -m venv pyvenv

. pyvenv/bin/activate

pip install -r app/requirements.txt
