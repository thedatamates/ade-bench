with source as (

    select * from {{ source('northwind', 'privileges') }}
)
select
    *
from source
