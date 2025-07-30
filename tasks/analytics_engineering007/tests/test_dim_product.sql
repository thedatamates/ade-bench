with checksum as (
  select 
    sum(1) as records,
    count(distinct product_id) as distinct_records,
    sum(standard_cost) as standard_cost_sum,
    sum(list_price) as list_price_sum,
    sum(len(product_code)) as product_code_length_sum  
  from dim_products
)

select *
from checksum
where records != 45
or round(distinct_records,0) != 45
or round(standard_cost_sum,0) != 454
or round(list_price_sum,0) != 617
or round(product_code_length_sum,0) != 353