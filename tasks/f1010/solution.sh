#!/bin/bash

file="analysis__lap_times.sql"

SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"
cp $SOLUTIONS_DIR/$file models/stats/$file

dbt run --select analysis__lap_times

