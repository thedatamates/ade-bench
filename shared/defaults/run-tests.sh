#!/bin/bash
source /scripts/setup-dbt-test.sh

# Pass through all arguments to run-dbt-test.sh
bash /scripts/run-dbt-test.sh "$@"
