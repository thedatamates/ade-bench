#!/bin/bash

# Update source schema in f1_dataset.yml file
yq -i '.sources[].schema = "public"' models/core/f1_dataset.yml

# Update STRFTIME
# s1="models/warehouse/fact_inventory.sql"
# f1="CAST(STRPTIME(transaction_created_date, '%m/%d/%Y %H:%M:%S') AS DATE)"
# r1="TO_DATE(TO_TIMESTAMP(transaction_created_date, 'MM/DD/YYYY HH24:MI:SS'))"

# sed -i "s|${f1}|${r1}|g" $s1

# s2="models/warehouse/fact_sales.sql"
# f2="CAST(STRPTIME(o.order_date, '%m/%d/%Y %H:%M:%S') AS DATE)"
# r2="TO_DATE(TO_TIMESTAMP(o.order_date, 'MM/DD/YYYY HH24:MI:SS'))"

# sed -i "s|${f2}|${r2}|g" $s2


# Update dim_dates spine
# MIGRATION_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/migrations"
# cp $MIGRATION_DIR/dim_date.sql models/warehouse/dim_date.sql