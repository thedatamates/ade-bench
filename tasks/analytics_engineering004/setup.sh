#!/bin/bash

# Remove a comma
rm -r models/analytics_obt
rm -r models/warehouse

dbt deps
dbt run