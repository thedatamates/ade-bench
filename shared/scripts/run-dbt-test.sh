#! /bin/bash
dbt deps
# remove any existing singular tests and add solution tests
rm -rf tests
mkdir tests
cp /tests/* tests

# run dbt data tests for evaluation
dbt test --select "test_type:singular"