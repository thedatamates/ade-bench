#!/bin/bash

# Update source schema in sources.yml file
yq -i '.sources[].schema = "public"' models/sources.yml

# Update configs in models
find='schema="main"'
replace='schema="public"'

files=(
    "models/agg/daily_agg_reviews.sql"
    "models/agg/mom_agg_reviews.sql"
    "models/agg/monthly_agg_reviews.sql"
    "models/agg/wow_agg_reviews.sql"
    "models/dim/dim_dates.sql"
    "models/dim/dim_hosts.sql"
    "models/dim/dim_listings.sql"
    "models/dim/dim_listings_hosts.sql"
    "models/fact/fct_reviews.sql"
)

for file in "${files[@]}"; do
    sed -i "s/${find}/${replace}/g" $file
done

# Update STRFTIME
find="STRFTIME('%m-%Y', REVIEW_DATE) AS MONTH_YEAR,"
replace="TO_CHAR(REVIEW_DATE, 'MM-YYYY') AS MONTH_YEAR,"
sed -i "s/${find}/${replace}/g" models/agg/monthly_agg_reviews.sql

# Update dim_dates spine
MIGRATION_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/migrations"
cp $MIGRATION_DIR/dim_dates.sql models/dim/dim_dates.sql