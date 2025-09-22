with source as (

    select * from {{ source('northwind', 'orders') }}
)
select
    *
from source
