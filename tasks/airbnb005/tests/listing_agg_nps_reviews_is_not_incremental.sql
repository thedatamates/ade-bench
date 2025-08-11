{% set model_name = 'listing_agg_nps_reviews' %}
{% set node = graph.nodes["model." ~ project_name ~ "." ~ model_name] %}
{% set mat = node.config.materialized %}

{% if mat != 'table' %}
    select 'Model is not materialized' as error_message
{% else %}
    select 1 where false
{% endif %}