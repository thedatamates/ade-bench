with checksum as (
  select 
    sum(1) as records,
    count(distinct inventory_id) as distinct_records,
    sum(inventory_id) as inventory_id_sum,
    sum(len(comments)) as comment_length_sum  
  from fact_inventory
)

select *
from checksum
where records != 102
or distinct_records != 102
or inventory_id_sum != 8721
or comment_length_sum != 504