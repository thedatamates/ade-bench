#!/bin/bash
## Change max to sum
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

## Note that not classifed is changed to unclassified
f1="position_desc = 'max("
r1="position_desc = 'sum("

"${SED_CMD[@]}" "s/${f1}/${r1}/g" models/stats/constructor_points.sql

# Run dbt to create the models
dbt run
