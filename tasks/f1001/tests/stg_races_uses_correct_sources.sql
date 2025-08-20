{% set model = "races" %}
{% set src_name = "src_" ~ model %}
{% set model_name = "stg_f1_dataset__" ~ model %}
{% set node = graph.nodes["model." ~ project_name ~ "." ~ model_name ] %}
{% set ref_list = node.refs %}

-- Model should have one source
{% if ref_list | length != 2 %}
    select '{{ model_name }} does not have two references' as error_message union all
{% elif 'stg_f1_dataset__circuits' not in ref_list | map(attribute='name') | list %}
    select '{{ model_name }} does not use stg_f1_dataset__circuits as source' as error_message union all
{% elif 'src_races' not in ref_list | map(attribute='name') | list %}
    select '{{ model_name }} does not use src_races as source' as error_message union all
{% endif %}

    select 'none' as error_message where false