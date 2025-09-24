with drivers as (
  select *
    from {{ ref('stg_f1_dataset__drivers') }}
),
results as (
  select *
    from {{ ref('stg_f1_dataset__results') }}
),
joined as (
  select d.driver_id,
         d.driver_full_name,
         r.position_desc
    from results as r
    join drivers as d
   using (driver_id)
),
grouped as (
  select driver_id,
         driver_full_name,
         sum(case when position_desc is null then 1 else 0 end) as finishes,
         sum(case when position_desc = 'disqualified' then 1 else 0 end) as disqualified,
         sum(case when position_desc = 'retired' then 1 else 0 end) as retired,
         sum(case when position_desc = 'excluded' then 1 else 0 end) as excluded,
         sum(case when position_desc = 'withdrew' then 1 else 0 end) as withdrew,
         sum(case when position_desc = 'failed to qualify' then 1 else 0 end) as failed_to_qualify,
         sum(case when position_desc = 'not classified' then 1 else 0 end) as not_classified,
    from joined
   group by 1, 2
),
final as (
  select rank() over (order by finishes desc) as rank,
         driver_full_name,
         finishes,
         excluded,
         withdrew,
         failed_to_qualify,
         disqualified,
         not_classified,
         retired
    from grouped
   order by finishes desc
   limit 120
)

select *
  from final