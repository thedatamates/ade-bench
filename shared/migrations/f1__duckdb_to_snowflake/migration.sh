#!/bin/bash

# Update source schema in f1_dataset.yml file
yq -i '.sources[].schema = "public"' models/core/f1_dataset.yml