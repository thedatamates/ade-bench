WITH source AS (
    SELECT *
    FROM {{ source('northwind', 'customer') }}
)
SELECT
    *
FROM source
