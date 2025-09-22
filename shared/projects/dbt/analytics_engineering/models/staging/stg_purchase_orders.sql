with source as (

    select * from {{ source('northwind', 'purchase_orders') }}
)
select
    *
from source
