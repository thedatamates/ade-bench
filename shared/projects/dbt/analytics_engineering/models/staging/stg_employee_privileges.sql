with source as (

    select * from {{ source('northwind', 'employee_privileges') }}
)
select
    *
from source