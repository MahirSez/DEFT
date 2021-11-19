#!/bin/bash


cd ../Network-Functions/NFs 
source venv/bin/activate

python perflow-packet-counter.py -i "h${1}-eth0" -f tcp


cd /media/mahir/New\ Volume/FT-Net/hazelCast
deactivate