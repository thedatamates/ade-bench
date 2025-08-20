{% set model_name = 'finishes_by_driver' %}
{% set node = graph.nodes["model." ~ project_name ~ "." ~ model_name ] %}
{% set ref_list = node.refs %}

    -- Model should have one source
{% if ref_list | length != 2 %}
    select '{{ model_name }} has more than one reference' as error_message union all
{% elif 'stg_f1_dataset__drivers' not in ref_list | map(attribute='name') | list %}
    select '{{ model_name }} does not use stg_f1_dataset__drivers as source' as error_message union all
{% elif 'stg_f1_dataset__results' not in ref_list | map(attribute='name') | list %}
    select '{{ model_name }} does not use stg_f1_dataset__results as source' as error_message union all
{% endif %}

    select 'none' as error_message where false