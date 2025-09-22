with source as (

    select * from {{ source('northwind', 'order_details') }}
)
select
    *
from source