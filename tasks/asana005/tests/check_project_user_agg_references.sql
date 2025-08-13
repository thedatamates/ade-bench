{% set table_name = "int_asana__project_user_agg" %}
{% set node = graph.nodes["model." ~ project_name ~ "." ~ table_name ] %}

{% set refs = node.refs | map(attribute='name') | map('lower') | list %}
{% set vars = node.vars | map(attribute='name') | map('lower') | list %}


-- Model should not reference old model
{% if "int_asana__project_user" not in refs %}
    select 'int_asana__project_user is not referenced and should be' as error_message union all
{% endif %}

-- Model should not old variable
{% if "user" in vars %}
    select 'user is not referenced in and should be' as error_message union all
{% endif %}

    select 'none' as error_message where false