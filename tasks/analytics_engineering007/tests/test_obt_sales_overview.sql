with checksums as (
  select 
    sum(1) as records,
    count(distinct o.product_id) as distinct_products,
    sum(len(product_code)) as product_code_length_sum
  from obt_sales_overview o
)

select * 
from checksums 
where round(records,0) != 58
  or round(distinct_products,0) != 20
  or round(product_code_length_sum,0) != 374