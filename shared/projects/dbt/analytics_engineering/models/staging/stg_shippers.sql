with source as (

    select * from {{ source('northwind', 'shippers') }}
)
select
    *
from source
