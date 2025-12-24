
with base as (

    select * 
    from {{ source('asana', 'team') }}

),

final as (
    
    select 
        id as team_id,
        name as team_name
    from base
    where not coalesce(_fivetran_deleted, false)
)

select * 
from final
