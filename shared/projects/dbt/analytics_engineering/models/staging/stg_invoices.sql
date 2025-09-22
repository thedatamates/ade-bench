with source as (

    select * from {{ source('northwind', 'invoices') }}
)
select
    *
from source
