{% set model_name = 'src_listings' %}
{% set node = graph.nodes["model." ~ project_name ~ "." ~ model_name] %}
{% set mat = node.config.materialized %}

{% if mat != 'view' %}
    select 'Model is not a view' as error_message
{% else %}
    select 1 where false
{% endif %}