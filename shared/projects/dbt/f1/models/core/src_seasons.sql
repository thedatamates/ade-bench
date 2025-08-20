{{
  config(
    materialized='view'
  )
}}

select * from {{ source('f1_dataset', 'seasons') }}
