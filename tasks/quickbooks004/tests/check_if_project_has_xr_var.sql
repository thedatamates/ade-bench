{% if var('using_exchange_rate',none) is not none %}
    {% if var('using_exchange_rate',none) is false %}
        select 'none' as error_message where false
    {% else %}
        select 'using_exchange_rate is set to True in dbt_project.yml' as error
    {% endif %}

{% else %}
    select 'There is no using_exchange_rate_variable in dbt_project.yml' as error
{% endif %}