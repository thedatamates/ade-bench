
with base as (

    select * 
    from {{ source('asana', 'project_task') }}

),

final as (
    
    select 
        project_id,
        task_id
    from base
)

select * 
from final
