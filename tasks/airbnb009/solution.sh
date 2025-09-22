#!/bin/bash
SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

file="mom_agg_reviews.sql"

# Update schema config in solution file by db type
if [[ "$*" == *"--db-type=duckdb"* ]]; then
    replace='schema="main"'
else
    replace='schema="public"'
fi

find='schema="main"'
sed -i "s/${find}/${replace}/g" $SOLUTIONS_DIR/$file

## Copy file with solution
cp $SOLUTIONS_DIR/$file models/agg/$file

# Run dbt to create the models
dbt run --select mom_agg_reviews --full-refresh