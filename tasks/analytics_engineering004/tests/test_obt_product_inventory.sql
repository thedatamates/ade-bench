with checksums as (
  select
    sum(o.product_id) as product_id_sum,
    sum(o.inventory_id) as inventory_id_sum,
    sum(o.quantity) as quantity_sum,
    sum(o.list_price) as list_price_sum,
    sum(1) as records
  from fact_inventory i
  left join dim_products p
    on p.product_id = i.product_id
  left join obt_product_inventory o
    on o.product_id = p.product_id
    and o.inventory_id = i.inventory_id
    and o.product_code = p.product_code
    and o.list_price = p.list_price
    and o.quantity_per_unit = p.quantity_per_unit
    and o.quantity = i.quantity
    order by 1
)

select * 
from checksums 
where round(product_id_sum,0) != 3292
  or round(inventory_id_sum,0) != 7367
  or round(quantity_sum,0) != 4955
  or round(list_price_sum,0) != 1585
  or round(records,0) != 102
 