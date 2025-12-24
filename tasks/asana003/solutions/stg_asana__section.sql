
with base as (

    select * 
    from {{ source('asana', 'section') }}

),

final as (
    
    select 
        id as section_id,
        cast(created_at as {{ dbt.type_timestamp() }}) as created_at,
        name as section_name,
        project_id
    from base
)

select * 
from final
