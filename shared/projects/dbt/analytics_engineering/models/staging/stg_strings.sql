with source as (

    select * from {{ source('northwind', 'strings') }}
)
select
    *
from source
