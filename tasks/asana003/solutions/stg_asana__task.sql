
with base as (

    select *
    from {{ source('asana', 'task') }}

),

final as (

    select
        id as task_id,
        assignee_id as assignee_user_id,
        completed as is_completed,
        cast(completed_at as {{ dbt.type_timestamp() }}) as completed_at,
        completed_by_id as completed_by_user_id,
        cast(created_at as {{ dbt.type_timestamp() }}) as created_at,
        cast(coalesce(due_on, due_at) as {{ dbt.type_timestamp() }}) as due_date,
        cast(modified_at as {{ dbt.type_timestamp() }}) as modified_at,
        name as task_name,
        parent_id as parent_task_id,
        cast(start_on as {{ dbt.type_timestamp() }}) as start_date,
        notes as task_description,
        cast(null as boolean) as is_liked,
        cast(null as integer) as number_of_likes,
        workspace_id
    from base
)

select *
from final
