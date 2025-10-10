with with_dates as (
    select
        *,
        extract(day from driver_date_of_birth) as bod_day,
        extract(month from driver_date_of_birth) as bod_month,
        extract(year from driver_date_of_birth) as bod_year,
        extract(day FROM CURRENT_DATE()) as now_day,
        extract(month FROM CURRENT_DATE()) as now_month,
        extract(year FROM CURRENT_DATE()) as now_year
    from {{ ref('stg_f1_dataset__drivers') }}
),

with_ages as (
    select
        *,
        (now_year - bod_year) -
            case when now_month < bod_month then 1
                 when now_month > bod_month then 0
                 when now_month = bod_month and now_day < bod_day then 1
                 else 0 end as current_age_in_years
    from with_dates
),

solution_key as (
    select
        current_age_in_years,
        count(*) as drivers
    from with_ages
    group by 1
),

combined as (
    select current_age_in_years, drivers from solution_key
    union
    -- This is hard-coded becasue dbt freaks out if it's a ref
    select current_age_in_years, drivers from analysis__drivers_current_age
),

count_solution_key as (
    select
        count(*) as solution_key_count,
        sum(drivers) as solution_key_drivers
    from solution_key
),

count_combined as (
    select
        count(*) as combined_count,
        sum(drivers) as combined_drivers
    from combined
)

select
    solution_key_count,
    combined_count
from count_solution_key
join count_combined
    on 1 = 1
where solution_key_count != combined_count
    or solution_key_drivers != combined_drivers