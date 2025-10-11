with answer as (
    select
        case when lower(answer) like '%b%' then FALSE else TRUE end as is_correct
    from {{ ref('analysis__answer') }}
)

select *
from answer
where is_correct = FALSE