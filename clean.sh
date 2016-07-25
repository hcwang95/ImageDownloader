#!/bin/bash

echo "start cleaning"

rm -r results/hsbc results/DBS results/citybank

# remember that it will hurt you if you forgot to move important things to other safe places
rm -r /home/hwang3/Downloads/*.txt
rm -r /home/hwang3/Downloads/*.crdownload

echo "already finished"