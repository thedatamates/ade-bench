with project_task_metrics as (

    select *
    from {{ ref('int_asana__project_task_metrics') }}
),

project as (
    
    select *
    from {{ var('project') }}
),

team as (
    select *
    from {{ var('team') }}
),

agg_sections as (
    select
        project_id,
        {{ fivetran_utils.string_agg( 'section_name', "', '") }} as sections

    from {{ var('section') }}
    where section_name != '(no section)'
    group by 1
),

project_user_agg as (

    select *
    from {{ ref('int_asana__project_user_agg') }}

),

project_join as (

    select
        project.project_id,
        project_name,

        coalesce(project_task_metrics.number_of_open_tasks, 0) as number_of_open_tasks,
        coalesce(project_task_metrics.number_of_assigned_open_tasks, 0) as number_of_assigned_open_tasks,
        coalesce(project_task_metrics.number_of_tasks_completed, 0) as number_of_tasks_completed,
        round(project_task_metrics.avg_close_time_days, 0) as avg_close_time_days,
        round(project_task_metrics.avg_close_time_assigned_days, 0) as avg_close_time_assigned_days,

        'https://app.asana.com/0/' || project.project_id ||'/' || project.project_id as project_link,

        project.team_id,
        team.team_name,
        project.is_archived,
        created_at,
        current_status,
        due_date,
        modified_at as last_modified_at,
        owner_user_id,
        project_user_agg.users as users_involved,
        coalesce(project_user_agg.number_of_users_involved, 0) as number_of_users_involved,
        agg_sections.sections,
        project.notes,
        project.is_public

    from
    project 
    left join project_task_metrics on project.project_id = project_task_metrics.project_id 
    left join project_user_agg on project.project_id = project_user_agg.project_id  
    join team on team.team_id = project.team_id -- every project needs a team
    left join agg_sections on project.project_id = agg_sections.project_id

)

select * from project_join