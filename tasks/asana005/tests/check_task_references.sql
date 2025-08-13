{% set table_name = "asana__project" %}
{% set node = graph.nodes["model." ~ project_name ~ "." ~ table_name ] %}

{% set refs = node.refs | map(attribute='name') | map('lower') | list %}
{% set vars = node.vars | map(attribute='name') | map('lower') | list %}


-- Model should use new model as reference
{% if "int_asana__project_user_agg" not in refs %}
    select 'int_asana__project_user_agg is not referenced and should be' as error_message union all
{% endif %}

-- Model should not reference old model
{% if "int_asana__project_user" in refs %}
    select 'int_asana__project_user is referenced and should not be' as error_message union all
{% endif %}

-- Model should not old variable
{% if "user" in vars %}
    select 'user is referenced and should not be' as error_message union all
{% endif %}

    select 'none' as error_message where false