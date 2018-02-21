#!/bin/bash
set -e
pip freeze --local | grep -v Competing-Approaches > requirements.txt
