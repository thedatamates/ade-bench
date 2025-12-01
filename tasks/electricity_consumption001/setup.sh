#!/bin/bash

dbt deps
dbt seed
dbt run

