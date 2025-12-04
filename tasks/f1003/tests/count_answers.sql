with answer as (
    select
        count(*) as answer_count
    from {{ ref('analysis__answer') }}
    where lower(answer) not like '%most_fastest_laps%'
)

select *
from answer
where answer_count != 3