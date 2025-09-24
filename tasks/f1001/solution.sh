#!/bin/bash
# Create src files
files=(
  "src_circuits.sql"
  "src_constructor_results.sql"
  "src_constructor_standings.sql"
  "src_constructors.sql"
  "src_driver_standings.sql"
  "src_drivers.sql"
  "src_lap_times.sql"
  "src_pit_stops.sql"
  "src_position_descriptions.sql"
  "src_qualifying.sql"
  "src_races.sql"
  "src_results.sql"
  "src_seasons.sql"
  "src_status.sql"
)

SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

for file in "${files[@]}"; do
  cp $SOLUTIONS_DIR/$file models/core/$file
done


## Udpdate staging models to point to src models
models=(
  "circuits"
  "constructor_results"
  "constructor_standings"
  "constructors"
  "driver_standings"
  "drivers"
  "lap_times"
  "pit_stops"
  "qualifying"
  "races"
  "results"
  "seasons"
  "status"
)

if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

for model in "${models[@]}"; do
  replace="ref('${model}')/ref('src_${model}')"
  path="models/staging/f1_dataset/stg_f1_dataset__${model}.sql"

  "${SED_CMD[@]}" "s/${replace}/g" "${path}"
done

## One-off updates to models
"${SED_CMD[@]}" "s/ref('status')/ref('src_status')/g" "models/staging/f1_dataset/stg_f1_dataset__results.sql"
"${SED_CMD[@]}" "s/ref('position_descriptions')/ref('src_position_descriptions')/g" "models/staging/f1_dataset/stg_f1_dataset__results.sql"
"${SED_CMD[@]}" "s/ref('position_descriptions')/ref('src_position_descriptions')/g" "models/stats/most_races.sql"

## Create new yaml file with correct schema
if [[ "$*" == *"--db-type=duckdb"* ]]; then
    schema="main"
else
    schema="public"
fi

cat > models/core/f1_dataset.yml << EOF
version: 2

sources:
  - name: f1_dataset
    schema: $schema
    tables:
      - name: circuits
      - name: constructors
      - name: constructor_standings
      - name: constructor_results
      - name: drivers
      - name: driver_standings
      - name: lap_times
      - name: pit_stops
      - name: position_descriptions
      - name: qualifying
      - name: races
      - name: results
      - name: seasons
      - name: status
EOF