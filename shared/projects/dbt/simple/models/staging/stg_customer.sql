WITH source AS (
    SELECT *
    FROM {{ source('simple', 'customer') }}
)
SELECT
    *
FROM source
