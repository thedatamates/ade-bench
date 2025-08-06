{% set uses_fallback = var('surrogate_key_treat_nulls_as_empty_strings',false) %}

{% if uses_fallback == true %}
    select 1 where false
{% else %}
    select 1    
{% endif %}