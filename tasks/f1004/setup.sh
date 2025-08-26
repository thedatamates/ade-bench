#!/bin/bash

## Update the string matches
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

## Note that not classifed is changed to unclassified
f1="position_desc = 'disqualified'"
f2="position_desc = 'excluded'"
f3="position_desc = 'failed to qualify'"
f4="position_desc = 'not classified'"
f5="position_desc = 'retired'"
f6="position_desc = 'withdrew'"

r1="position_desc = 'Disqualified'"
r2="position_desc = 'Excluded'"
r3="position_desc = 'Failed to Qualify'"
r4="position_desc = 'Unclassified'"
r5="position_desc = 'Retired'"
r6="position_desc = 'Withdrew'"

"${SED_CMD[@]}" "s/${f1}/${r1}/g" models/stats/finishes_by_driver.sql
"${SED_CMD[@]}" "s/${f2}/${r2}/g" models/stats/finishes_by_driver.sql
"${SED_CMD[@]}" "s/${f3}/${r3}/g" models/stats/finishes_by_driver.sql
"${SED_CMD[@]}" "s/${f4}/${r4}/g" models/stats/finishes_by_driver.sql
"${SED_CMD[@]}" "s/${f5}/${r5}/g" models/stats/finishes_by_driver.sql
"${SED_CMD[@]}" "s/${f6}/${r6}/g" models/stats/finishes_by_driver.sql

dbt run