#!/bin/bash
## Fix the left join
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

f1="join"
r1="left join"

"${SED_CMD[@]}" "s/${f1}/${r1}/g" models/staging/f1_dataset/stg_f1_dataset__results.sql

# Run dbt to create the models
dbt run
