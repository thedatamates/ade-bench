#!/bin/bash

## Add broken agg.yml to agg directory
SETUP_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/setup"

cp $SETUP_DIR/agg.yml models/agg/agg.yml