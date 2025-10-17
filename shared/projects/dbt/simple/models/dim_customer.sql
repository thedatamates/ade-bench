WITH stg_customer AS (
    SELECT *
    FROM {{ ref('stg_customer') }}
)
SELECT
    *
FROM stg_customer
