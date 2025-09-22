#!/bin/bash
# Set schema based on database type
if [[ "$*" == *"--db-type=duckdb"* ]]; then
    schema="main"
else
    schema="public"
fi

########################################################
# Update source models to be be views

cat <<EOF | cat - models/source/src_hosts.sql > tmp && mv tmp models/source/src_hosts.sql
{{
	config(
		materialized="view" ,
		alias="src_hosts" ,
		schema="$schema" ,
		unique_key="HOST_ID"
	)
}}

EOF

cat <<EOF | cat - models/source/src_listings.sql > tmp && mv tmp models/source/src_listings.sql
{{
	config(
		materialized="view" ,
		alias="src_listings" ,
		schema="$schema" ,
		unique_key="LISTING_ID"
	)
}}

EOF

cat <<EOF | cat - models/source/src_reviews.sql > tmp && mv tmp models/source/src_reviews.sql
{{
	config(
		materialized="view" ,
		alias="src_reviews" ,
		schema="$schema" ,
		unique_key="LISTING_ID"
	)
}}

EOF