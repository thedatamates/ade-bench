with answer as (
    select
        max(case when lower(answer) like '%oldest_race_winners_in_modern_era%' then 1 else 0 end) as is_correct
    from {{ ref('analysis__answer') }}
)

select *
from answer
where is_correct != 1