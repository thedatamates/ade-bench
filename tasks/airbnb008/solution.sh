#!/bin/bash
SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

cp $SOLUTIONS_DIR/agg.yml models/agg/agg.yml

dbt deps
dbt run
