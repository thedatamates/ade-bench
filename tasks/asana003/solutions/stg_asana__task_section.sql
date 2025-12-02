
with base as (

    select * 
    from {{ source('asana', 'task_section') }}

),

final as (
    
    select 
        section_id,
        task_id
    from base
)

select * 
from final
