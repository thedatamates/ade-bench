#!/bin/bash

rm models/stats/__stats.yml
rm models/stats/most_wins.sql
rm models/stats/most_retirements.sql

dbt deps
dbt run