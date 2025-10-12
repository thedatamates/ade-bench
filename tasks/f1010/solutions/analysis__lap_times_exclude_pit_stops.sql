with
  laps as (
    select
      l.race_id,
      l.driver_id,
      l.milliseconds as lap_time,
      r.race_year,
      r.circuit_id,
      r.circuit_name,
      case when p.race_id is null then 0 else 1 end as has_pit_stop,
    from {{ ref('stg_f1_dataset__lap_times') }} l
    left join {{ ref('stg_f1_dataset__races') }}     r
      on r.race_id = l.race_id
    left join {{ ref('stg_f1_dataset__pit_stops') }} p
      on p.race_id = l.race_id
      and p.driver_id = l.driver_id
      and p.lap = l.lap
  ),

  metrics as (
    select
      l.circuit_name,
      l.circuit_id,
      l.race_year,
      avg(l.lap_time) as avg_lap_time,
    from laps l
    where l.has_pit_stop = 0
    group by 1,2,3
  )

    select
      m.circuit_name,
      m.race_year,
      cast(round(m.avg_lap_time,0) as integer) as avg_lap_time_in_ms
    from metrics m
    order by 1,2