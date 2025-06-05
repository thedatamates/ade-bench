#! /bin/bash
dbt deps
pwd
ls
mkdir tests
cp /tests/test_* tests
ls
ls tests
dbt test