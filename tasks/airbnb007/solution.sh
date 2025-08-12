#!/bin/bash
SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

cp $SOLUTIONS_DIR/dim_hosts.sql models/dim_hosts.sql
cp $SOLUTIONS_DIR/dim_listings.sql models/dim_listings.sql
cp $SOLUTIONS_DIR/dim_listings_hosts.sql models/dim_listings_hosts.sql
cp $SOLUTIONS_DIR/fct_reviews.sql models/fct_reviews.sql
cp $SOLUTIONS_DIR/daily_agg_nps_reviews.sql models/daily_agg_nps_reviews.sql
cp $SOLUTIONS_DIR/listing_agg_nps_reviews.sql models/listing_agg_nps_reviews.sql

dbt deps
dbt run
