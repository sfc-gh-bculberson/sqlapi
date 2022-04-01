#!/bin/bash
set -m

export AUTHTOKEN=`python3 ./generate-api-jwt.py`
export ACCOUNT=SFSENORTHAMERICA_DEMO226
locust -f run.py Queries --master &
WORKERS=`getconf _NPROCESSORS_ONLN`
until [ $WORKERS -lt 0 ]; do
    locust -f run.py --worker &
    let WORKERS-=1
done
fg %1
pkill locust