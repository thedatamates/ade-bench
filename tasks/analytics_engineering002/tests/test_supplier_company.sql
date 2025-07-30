with matches as (
  select count(*) as cols 
  from "information_schema"."columns"
  where table_name = 'obt_product_inventory'
    and column_name in (
      'description',
      'supplier_company',
      'standard_cost',
      'dummy'
    )
)

select * 
from matches 
where cols != 3