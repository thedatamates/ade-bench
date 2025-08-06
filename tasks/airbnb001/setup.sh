#!/bin/bash

## Replace all generate_surrogate_key functions with deprecated surrogate_key
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

"${SED_CMD[@]}" 's/generate_surrogate_key/surrogate_key/g' models/agg/daily_agg_reviews.sql
"${SED_CMD[@]}" 's/generate_surrogate_key/surrogate_key/g' models/agg/mom_agg_reviews.sql
"${SED_CMD[@]}" 's/generate_surrogate_key/surrogate_key/g' models/agg/monthly_agg_reviews.sql
"${SED_CMD[@]}" 's/generate_surrogate_key/surrogate_key/g' models/agg/wow_agg_reviews.sql
"${SED_CMD[@]}" 's/generate_surrogate_key/surrogate_key/g' models/dim/dim_listings_hosts.sql

dbt deps
dbt run