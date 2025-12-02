
with base as (

    select * 
    from {{ source('asana', 'user') }}

),

final as (
    
    select 
        id as user_id,
        email,
        name as user_name
    from base
    where not coalesce(_fivetran_deleted, false)
)

select * 
from final
