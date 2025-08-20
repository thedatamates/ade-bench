{% set sources = [
    "circuits",
    "constructor_results",
    "constructor_standings",
    "constructors",
    "driver_standings",
    "drivers",
    "lap_times",
    "pit_stops",
    "position_descriptions",
    "qualifying",
    "races",
    "results",
    "seasons",
    "status"
] %}

{% for source in sources %}
    {% set src_name = "src_" ~ source %}
    {% set node = graph.nodes["model." ~ project_name ~ "." ~ src_name ] %}
    {% set src_list = node.sources %}
    {% set mat = node.config.materialized %}

    {% if mat != "view" %}
        select '{{ src_name }} is not a view and should be' as error_message union all
    {% endif %}

    -- Model should have one source
    {% if src_list | length != 1 %}
        select '{{ src_name }} has more than one source' as error_message union all
    {% elif src_list[0][1] != source %}
        select '{{ src_name }} does not use {{ source}} as source' as error_message union all
    {% endif %}
{% endfor %}

        select 'none' as error_message where false