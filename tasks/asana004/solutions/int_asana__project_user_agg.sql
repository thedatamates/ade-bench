with project_user as (
    
    select *
    from {{ ref('int_asana__project_user') }}
),

asana_user as (
    select *
    from {{ var('user') }}
),

agg_project_users as (

    select 
        project_user.project_id,
        {{ fivetran_utils.string_agg( "asana_user.user_name || ' as ' || project_user.role" , "', '" ) }} as users

    from project_user join asana_user using(user_id)

    group by 1
),

-- need to split from above due to redshift's inability to string/list_agg and use distinct aggregates
count_project_users as (
 
    select 
        project_id, 
        count(distinct user_id) as number_of_users_involved

    from project_user
    group by 1

),

project_user_join as (

    select
        agg.project_id,
        agg.users,
        cnt.number_of_users_involved
    from
    agg_project_users agg
    left join count_project_users cnt on cnt.project_id = agg.project_id

)

select * from project_user_join