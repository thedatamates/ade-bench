#!/bin/bash
SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

## Update schema config in solution files by db type
files=(
    "dim_hosts.sql"
    "dim_listings.sql"
    "dim_listings_hosts.sql"
    "fct_reviews.sql"
    "daily_agg_nps_reviews.sql"
    "listing_agg_nps_reviews.sql"
)

if [[ "$*" == *"--db-type=duckdb"* ]]; then
    replace='schema="main"'
else
    replace='schema="public"'
fi

for file in "${files[@]}"; do
    find='schema="main"'
    sed -i "s/${find}/${replace}/g" $SOLUTIONS_DIR/$file
done

## Copy solution files
for file in "${files[@]}"; do
    cp $SOLUTIONS_DIR/$file models/$file
done

## Run dbt
dbt deps
dbt run
