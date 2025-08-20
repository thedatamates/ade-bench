{{
  config(
    materialized='view'
  )
}}

select * from {{ source('f1_dataset', 'lap_times') }}
