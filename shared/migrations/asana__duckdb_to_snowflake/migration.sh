#!/bin/bash

## Update profile.yml file
MIGRATION_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/migration"
cp $MIGRATION_DIR/"profiles.yml" "profiles.yml"


## Update primary schema in dbt_project.yml file
if [[ "$OSTYPE" == "darwin"* ]]; then
  SED_CMD=(sed -i '')
else
  SED_CMD=(sed -i)
fi

find="asana_schema: main"
replace="asana_schema: public"

"${SED_CMD[@]}" "s/${find}/${replace}/g" dbt_project.yml

