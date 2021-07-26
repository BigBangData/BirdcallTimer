#!/bin/bash
# activate env from source 
# and run python unbuffered to print to console
source activate py38
python -u app.py $1 $2 $3 $4