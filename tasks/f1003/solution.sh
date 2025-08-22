#!/bin/bash
## Remove limit and add final where clause
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi
 
 ## Files with limit 20
files=(
  "most_fastest_laps.sql"
  "most_laps.sql"
  "most_podiums.sql"
  "most_pole_positions.sql"
  "most_retirements.sql"
  "most_wins.sql"
)

for file in "${files[@]}"; do
  "${SED_CMD[@]}" "s/limit 20//g" models/stats/$file
  echo " where rank <= 20" >> models/stats/$file
done

## Remove limit 120 from most races
"${SED_CMD[@]}" "s/limit 120//g" models/stats/most_races.sql
echo " where rank <= 120" >> models/stats/most_races.sql

# Run dbt to create the models
dbt run
