#!/bin/bash

## Replace all generate_surrogate_key functions with deprecated surrogate_key
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

"${SED_CMD[@]}" 's/src_reviews_cte/src_listings_cte/g' models/fact/fct_reviews.sql

dbt deps
dbt run