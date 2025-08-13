#!/bin/bash

## Fix the error by changing the data type of the underlying table. 
## MOVE FILES
SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

project="asana__project.sql"
agg="int_asana__project_user_agg.sql"

cp $SOLUTIONS_DIR/$project models/$project
cp $SOLUTIONS_DIR/$agg models/intermediate/$agg


dbt run
