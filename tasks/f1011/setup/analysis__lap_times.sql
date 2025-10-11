with
  laps as (
    select
      l.race_id,
      l.driver_id,
      l.lap,
      l.milliseconds as lap_time,
      r.race_year,
      r.circuit_id,
      r.circuit_name,
      p.stop,
      coalesce(p.seconds,0) as pit_time,
      l.milliseconds - coalesce(p.seconds,0) * 1000 as adjusted_lap_time
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
      avg(l.adjusted_lap_time) as avg_adjusted_lap_time,
      avg(l.pit_time) as avg_pit_time
    from laps l
    group by 1,2,3
  )

    select
      m.circuit_name,
      m.race_year,
      cast(round(m.avg_lap_time,0) as integer) as avg_lap_time_in_ms
    from metrics m
    order by 1,2