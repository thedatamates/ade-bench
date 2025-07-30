with totals as (
  select 
    count(*) as col_count,
    count(customer_id) as customer_id_count,
    count(distinct customer_id) as distinct_customer_id_count
  from dim_customer
)

select * 
from totals
where col_count != 29
  or customer_id_count != 29
  or distinct_customer_id_count != 29