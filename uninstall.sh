#!/bin/bash

clear
echo "[ ... ] Removing package and dependencies..."
python3 -m pip uninstall -r requirements.txt
rm -r ../pisco
sleep 2
