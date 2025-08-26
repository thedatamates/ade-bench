#!/bin/bash
## Remove limit and add final where clause
## Update the string matches
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

## Note that not classifed is changed to unclassified
f1="position_desc = 'Disqualified'"
f2="position_desc = 'Excluded'"
f3="position_desc = 'Failed to Qualify'"
f4="position_desc = 'Unclassified'"
f5="position_desc = 'Retired'"
f6="position_desc = 'Withdrew'"

r1="position_desc = 'disqualified'"
r2="position_desc = 'excluded'"
r3="position_desc = 'failed to qualify'"
r4="position_desc = 'not classified'"
r5="position_desc = 'retired'"
r6="position_desc = 'withdrew'"

"${SED_CMD[@]}" "s/${f1}/${r1}/g" models/stats/finishes_by_driver.sql
"${SED_CMD[@]}" "s/${f2}/${r2}/g" models/stats/finishes_by_driver.sql
"${SED_CMD[@]}" "s/${f3}/${r3}/g" models/stats/finishes_by_driver.sql
"${SED_CMD[@]}" "s/${f4}/${r4}/g" models/stats/finishes_by_driver.sql
"${SED_CMD[@]}" "s/${f5}/${r5}/g" models/stats/finishes_by_driver.sql
"${SED_CMD[@]}" "s/${f6}/${r6}/g" models/stats/finishes_by_driver.sql

# Run dbt to create the models
dbt run --select finishes_by_driver
