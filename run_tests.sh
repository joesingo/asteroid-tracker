#!/bin/bash
dir=$(dirname $0)
min_coverage=90
coverage run --source asteroid_tracker -m pytest ${dir}/asteroid_tracker/tests.py $* \
    && (coverage report -m --fail-under=$min_coverage || echo -e "\nCoverage is looking a bit low...")
