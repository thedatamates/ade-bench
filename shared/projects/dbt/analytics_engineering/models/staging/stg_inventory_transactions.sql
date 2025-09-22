with source as (

    select * from {{ source('northwind', 'inventory_transactions') }}
)
select
    *
from source