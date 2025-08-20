#!/bin/bash
SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

## Copy file with solution
cp $SOLUTIONS_DIR/mom_agg_reviews.sql models/agg/mom_agg_reviews.sql

# Run dbt to create the models
dbt run --select mom_agg_reviews --full-refresh
