with checksum as (
    select 
        min(aggregation_date) as min_date,
        max(aggregation_date) as max_date,
        count(*) as review_days,
        sum(review_totals) as review_totals
    from mom_agg_reviews
    where aggregation_date >= '2009-06-20'
    and aggregation_date <= '2021-10-22'
)

select * 
from checksum
where min_date != '2009-06-20'
    or max_date != '2021-10-22'
    or review_days != 12278
    or review_totals != 12196400


