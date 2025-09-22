#!/bin/bash

# Update source schema in sources.yml file
yq -i '.sources[].schema = "public"' models/staging/source.yml

# Update dim_dates spine
MIGRATION_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/migrations"
cp $MIGRATION_DIR/dim_date.sql models/warehouse/dim_date.sql