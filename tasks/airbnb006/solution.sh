#!/bin/bash

## Replace all generate_surrogate_key functions with deprecated surrogate_key
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

"${SED_CMD[@]}" 's/src_listings_cte/src_reviews_cte/g' models/fact/fct_reviews.sql
"${SED_CMD[@]}" 's/src_listings_cte/src_hosts_cte/g' models/dim/dim_hosts.sql

dbt deps