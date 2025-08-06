#!/bin/bash
cat > models/source/src_hosts.sql << 'EOF'
WITH RAW_HOSTS AS (
	SELECT *
	FROM {{source('airbnb','hosts')}}
)

SELECT
	ID AS HOST_ID ,
	NAME AS HOST_NAME ,
	IS_SUPERHOST ,
	CREATED_AT ,
	UPDATED_AT 
FROM 
	RAW_HOSTS
EOF

cat > models/source/src_listings.sql << 'EOF'
WITH RAW_LISTINGS AS (
	SELECT *
	FROM {{source('airbnb','listings')}}
)

SELECT
	  ID AS LISTING_ID ,
	  NAME AS LISTING_NAME ,
	  LISTING_URL ,
	  ROOM_TYPE ,
	  MINIMUM_NIGHTS ,
	  HOST_ID ,
	  PRICE AS PRICE_STR ,
	  CREATED_AT ,
	  UPDATED_AT 
FROM
	RAW_LISTINGS
EOF

cat > models/source/src_reviews.sql << 'EOF'
WITH RAW_REVIEWS AS (
	SELECT * 
	FROM {{source('airbnb','reviews')}}
)

SELECT
	LISTING_ID ,
	DATE AS REVIEW_DATE ,
	REVIEWER_NAME ,
	COMMENTS AS REVIEW_TEXT ,
	SENTIMENT AS REVIEW_SENTIMENT 
FROM
	RAW_REVIEWS
EOF

dbt deps
dbt run