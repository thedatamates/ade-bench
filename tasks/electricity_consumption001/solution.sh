#!/bin/bash

# Get the absolute path to the solutions directory
SOLUTIONS_DIR="$(dirname "$(readlink -f "${BASH_SOURCE}")")/solutions"

# Copy the hourly_rates model from solutions directory
cp $SOLUTIONS_DIR/hourly_rates.sql models/hourly_rates.sql

dbt run --select hourly_rates
dbt deps