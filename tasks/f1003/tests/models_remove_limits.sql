{% set models = [
    "most_fastest_laps",
    "most_laps",
    "most_podiums",
    "most_pole_positions",
    "most_races",
    "most_retirements",
    "most_wins",
    "oldest_race_winners_in_modern_era"
] %}

{% for model_name in models %}
    {% set node = graph.nodes["model." ~ project_name ~ "." ~ model_name ] %}
    {% set raw_sql = node.raw_code %}

    -- Model should have one source
    {% if "limit" in raw_sql %}
        select '{{ model_name }} still has a limit' as error_message union all
    {% endif %}
{% endfor %}

        select 'none' as error_message where false