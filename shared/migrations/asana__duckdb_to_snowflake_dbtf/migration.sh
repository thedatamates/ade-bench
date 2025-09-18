#!/bin/bash

# Update primary schema in dbt_project.yml file
yq -i '.vars.asana_schema = "public"' dbt_project.yml

# Update configs for deprecated stuff
MIGRATION_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/migrations"

cp $MIGRATION_DIR/asana.yml models/asana.yml
cp $MIGRATION_DIR/intermediate_asana.yml models/intermediate/intermediate_asana.yml

# Comment out bad key
find="+all_varchar: true"
replace="# +all_varchar: true"
sed -i "s/${find}/${replace}/g" dbt_project.yml