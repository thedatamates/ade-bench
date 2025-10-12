#!/bin/bash

# Update primary schema in dbt_project.yml file
yq -i '.vars.workday_schema = "public"' dbt_project.yml



# Update schema files for dbt fusion deprecations
MIGRATION_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/migrations"

cp $MIGRATION_DIR/workday.yml models/workday.yml
cp $MIGRATION_DIR/stg_workday.yml models/staging/stg_workday.yml