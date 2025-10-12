#!/bin/bash

# Update primary schema in dbt_project.yml file
yq -i '.vars.workday_schema = "public"' dbt_project.yml