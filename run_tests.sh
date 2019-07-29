#!/bin/bash
dir=$(dirname $0)
coverage run --source asteroid_tracker -m pytest ${dir}/asteroid_tracker/tests.py $* \
    && coverage report -m
