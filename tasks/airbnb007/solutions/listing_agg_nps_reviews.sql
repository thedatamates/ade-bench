{{
	config(
		materialized="table" ,
		alias="listing_agg_nps_reviews" ,
		schema="main"
	)
}}

with with_nps_scores as (
  select 
    listing_id,
    case 
      when review_sentiment = 'positive' then 1
      when review_sentiment = 'negative' then -1
      else 0 end as nps_score
  from {{ ref('fct_reviews') }} r    
),

final as (
  select
    l.listing_id,
    l.listing_name,
    l.room_type,
    avg(s.nps_score) as nps_total,
    count(s.listing_id) as reviews_total,
  from {{ ref('dim_listings') }} l 
  join with_nps_scores s
    on s.listing_id = l.listing_id
  group by 1,2,3
)

select * from final
