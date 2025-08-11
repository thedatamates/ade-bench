{% set model_name = 'dim_listings' %}
{% set node = graph.nodes["model." ~ project_name ~ "." ~ model_name] %}
{% set raw_sql = node.raw_code %}

{% if "src_listings_cte" not in raw_sql %}
    select 'CTE unnecessarily updated' as error_message
{% else %}
    select 1 where false
{% endif %}