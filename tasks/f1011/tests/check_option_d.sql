with answer as (
    select
        case when lower(answer) like '%d%' then TRUE else FALSE end as is_correct
    from {{ ref('analysis__answer') }}
)

select *
from answer
where is_correct = FALSE