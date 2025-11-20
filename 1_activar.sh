#!/bin/bash

. pyvenv/bin/activate

cd app/

python server.py --host 127.0.0.1 --port 5555 --folder_watch ../codigos_editables
