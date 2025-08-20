{{
  config(
    materialized='view'
  )
}}

select * from {{ source('f1_dataset', 'qualifying') }}
