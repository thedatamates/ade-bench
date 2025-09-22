#!/bin/bash
# Set schema based on database type
if [[ "$*" == *"--db-type=duckdb"* ]]; then
    schema="main"
else
    schema="public"
fi

## Add the primary key to the fct_reviews model
cat > models/fact/fct_reviews.sql << EOF
{{
	config(
		materialized="incremental" ,
		alias="fct_reviews" ,
		schema="$schema"
	)
}}

WITH src_reviews_cte AS (
	SELECT *
	FROM {{ref('src_reviews')}}
)

SELECT
	{{dbt_utils.generate_surrogate_key(['LISTING_ID','REVIEW_DATE','REVIEWER_NAME','REVIEW_TEXT'])}} AS REVIEW_ID,
	*
FROM src_reviews_cte
WHERE REVIEW_TEXT IS NOT NULL

{% if is_incremental() %}
	AND REVIEW_DATE > (SELECT MAX(REVIEW_DATE)
					   FROM {{ this}}
					   )
{% endif %}
EOF

# Run dbt to create the models
dbt run --select fct_reviews --full-refresh