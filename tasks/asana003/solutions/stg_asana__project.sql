
with base as (

    select * 
    from {{ source('asana', 'project') }}

),

final as (
    
    select 
        id as project_id,
        archived as is_archived,
        cast(created_at as {{ dbt.type_timestamp() }}) as created_at,
        current_status,
        cast(due_date as {{ dbt.type_timestamp() }}) as due_date,
        cast(modified_at as {{ dbt.type_timestamp() }}) as modified_at,
        name as project_name,
        owner_id as owner_user_id,
        public as is_public,
        team_id,
        workspace_id,
        notes
    from base
)

select * 
from final
