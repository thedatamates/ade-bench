#!/bin/bash

# Update source schema in sources.yml file
yq -i '.sources[].schema = "public"' models/staging/source.yml