with lap_times as (
  select raceId as race_id,
         driverId as driver_id,
         lap,
         position,
         time,
         milliseconds
    from {{ ref('src_lap_times') }}
)

select *
  from lap_times