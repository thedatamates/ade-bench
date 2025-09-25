#!/bin/bash

# Update source schema in the dbt_project.yml file
yq -i '.vars.intercom_schema = "public"' dbt_project.yml