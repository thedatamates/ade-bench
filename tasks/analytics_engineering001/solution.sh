#!/bin/bash

# Run dbt to create the models
dbt run --select obt_product_inventory
