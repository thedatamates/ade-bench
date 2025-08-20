{% set models = [
    "most_fastest_laps",
    "most_podiums",
    "most_pole_positions"
] %}

{% for model_name in models %}
    {% set node = graph.nodes["model." ~ project_name ~ "." ~ model_name ] %}
    {% set ref_list = node.refs %}

    -- Model should have one source
    {% if ref_list | length != 1 %}
        select '{{ model_name }} has more than one reference' as error_message union all
    {% elif ref_list | map(attribute='name') | first != 'finishes_by_driver' %}
        select '{{ model_name }} does not use finishes_by_driver as source' as error_message union all
    {% endif %}
{% endfor %}

        select 'none' as error_message where false