{{ config(enabled=var('asana__using_tags', True)) }}

with base as (

    select * 
    from {{ source('asana', 'tag') }}

),

final as (
    
    select 
        id as tag_id,
        name as tag_name,
        cast(created_at as {{ dbt.type_timestamp() }}) as created_at
    from base
    where not _fivetran_deleted
)

select * 
from final