# Profiling Data

## Get metadata about a single column

Investigate a single column using a query like this. Be mindful of warehouse compute consumption when deciding how many of these queries to run.

```sql
select
    min(product_id) as min_value,
    max(product_id) as max_value,
    count(product_id) as count_not_null,
    count(distinct product_id) as count_unique_values,
    count(*) as count_rows,
    min(length(product_id)) as shortest_value,
    max(length(product_id)) as longest_value,
from {{ ref('my_model') }}
```
