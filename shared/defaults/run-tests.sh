#!/bin/bash

source $TEST_DIR/setup-dbt-test.sh

# Pass through all arguments to run-dbt-test.sh
bash $TEST_DIR/run-dbt-test.sh "$@"
