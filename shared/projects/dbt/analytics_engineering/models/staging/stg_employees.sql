with source as (

    select * from {{ source('northwind', 'employees') }}
)
select
    *
from source