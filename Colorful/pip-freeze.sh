#!/bin/bash
set -e
# Freeze dependencies, except:
# * caffe (we want to use the system site package if available)
# * colorful-dependencies
pip freeze --local | grep -v -e colorful-dependencies -e caffe > requirements.txt
