with checksum as (
  select 
    sum(1) as records,
    count(distinct order_id) as distinct_orders,
    count(distinct product_id) as distinct_products,
    sum(customer_id) as customer_id_sum,
    sum(employee_id) as employee_id_sum
  from fact_sales
)

select *
from checksum
where records != 58
or distinct_orders != 40
or distinct_products != 24
or customer_id_sum != 689
or employee_id_sum != 233