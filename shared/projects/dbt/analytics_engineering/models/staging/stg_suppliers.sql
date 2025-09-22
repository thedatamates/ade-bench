with source as (

    select * from {{ source('northwind', 'suppliers') }}
)
select
    *
from source
