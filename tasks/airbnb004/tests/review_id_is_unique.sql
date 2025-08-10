with temp as (
    select 
        count(1) as total_rows,
        count(review_id) as total_review_ids,
        count(distinct review_id) as distinct_review_ids
    from fct_reviews
)

select * from temp
where 
    total_rows != total_review_ids
    or total_review_ids != distinct_review_ids
