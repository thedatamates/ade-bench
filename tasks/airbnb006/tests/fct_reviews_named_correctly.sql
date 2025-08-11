{% set model_name = 'fct_reviews' %}
{% set node = graph.nodes["model." ~ project_name ~ "." ~ model_name] %}
{% set raw_sql = node.raw_code %}

{% if "src_listings_cte" in raw_sql %}
    select 'CTE not updated' as error_message
{% else %}
    select 1 where false
{% endif %}