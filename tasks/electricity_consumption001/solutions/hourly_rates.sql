with days as (
    select unnest([0, 1, 2, 3, 4, 5, 6]) as day_of_week
),

hours as (
    select unnest(range(0, 24)) as hour
),

rate_plans_expanded as (
    select
        retailer,
        plan_name,
        rate_name,
        start_hour,
        end_hour,
        applies_weekday,
        applies_weekend,
        price_per_kwh,
        daily_charge
    from {{ ref('rate_plans') }}
),

cartesian as (
    select
        rp.retailer,
        rp.plan_name,
        rp.rate_name,
        d.day_of_week,
        h.hour,
        rp.start_hour,
        rp.end_hour,
        rp.applies_weekday,
        rp.applies_weekend,
        rp.price_per_kwh,
        rp.daily_charge
    from rate_plans_expanded rp
    cross join days d
    cross join hours h
),

filtered as (
    select
        retailer,
        plan_name,
        day_of_week,
        hour,
        price_per_kwh,
        daily_charge
    from cartesian
    where
        -- Hour must be within the rate's time range
        hour >= start_hour
        and hour <= end_hour
        -- Day type must match
        and (
            (day_of_week in (1, 2, 3, 4, 5) and applies_weekday)
            or (day_of_week in (0, 6) and applies_weekend)
        )
)

select
    retailer,
    plan_name,
    day_of_week,
    hour,
    price_per_kwh,
    daily_charge
from filtered
order by retailer, plan_name, day_of_week, hour

