#!/bin/bash
# Create the product_performance model
cat <<EOF | cat - models/source/src_hosts.sql > tmp && mv tmp models/source/src_hosts.sql
{{
	config(
		materialized="view" ,
		alias="src_hosts" ,
		schema="main" ,
		unique_key="HOST_ID"
	)
}}

EOF

cat <<EOF | cat - models/source/src_listings.sql > tmp && mv tmp models/source/src_listings.sql
{{
	config(
		materialized="view" ,
		alias="src_listings" ,
		schema="main" ,
		unique_key="LISTING_ID"
	)
}}

EOF

cat <<EOF | cat - models/source/src_reviews.sql > tmp && mv tmp models/source/src_reviews.sql
{{
	config(
		materialized="view" ,
		alias="src_reviews" ,
		schema="main" ,
		unique_key="LISTING_ID"
	)
}}

EOF