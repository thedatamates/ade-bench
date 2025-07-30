with checksum as (
  select 
    sum(1) as records,
    count(distinct product_id) as distinct_records,
    sum(product_id) as product_id_sum,
    sum(standard_cost) as standard_cost_sum,
    sum(list_price) as list_price_sum,
    sum(len(product_code)) as product_code_length_sum  
  from dim_products
)

select *
from checksum
where records != 40
or round(distinct_records,0) != 40
or round(product_id_sum,0) != 2450
or round(standard_cost_sum,0) != 387
or round(list_price_sum,0) != 528
or round(product_code_length_sum,0) != 315