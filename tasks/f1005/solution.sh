#!/bin/bash
## Change sum back to max
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

## Note that not classifed is changed to unclassified
f1="position_desc = 'sum("
r1="position_desc = 'max("

"${SED_CMD[@]}" "s/${f1}/${r1}/g" models/stats/constructor_points.sql

# Run dbt to create the models
dbt run --select constructor_points
