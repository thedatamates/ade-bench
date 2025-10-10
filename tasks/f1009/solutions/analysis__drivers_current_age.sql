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
)

select
    current_age_in_years,
    count(*) as drivers
from with_ages
group by 1
order by 1