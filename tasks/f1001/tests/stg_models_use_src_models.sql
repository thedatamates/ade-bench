{% set models = [
    "circuits",
    "constructor_results",
    "constructor_standings",
    "constructors",
    "driver_standings",
    "drivers",
    "lap_times",
    "pit_stops",
    "qualifying",
    "seasons",
    "status"
] %}

{% for model in models %}
    {% set src_name = "src_" ~ model %}
    {% set model_name = "stg_f1_dataset__" ~ model %}
    {% set node = graph.nodes["model." ~ project_name ~ "." ~ model_name ] %}
    {% set ref_list = node.refs %}

    -- Model should have one source
    {% if ref_list | length != 1 %}
        select '{{ model_name }} has more than one reference' as error_message union all
    {% elif ref_list | map(attribute='name') | first != src_name %}
        select '{{ model_name }} does not use {{ src_name }} as source' as error_message union all
    {% endif %}
{% endfor %}

        select 'none' as error_message where false