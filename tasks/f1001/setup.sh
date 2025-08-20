#!/bin/bash

rm -r models/stats

dbt deps
dbt run