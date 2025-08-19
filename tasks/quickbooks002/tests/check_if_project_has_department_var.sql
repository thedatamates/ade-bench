{% if var('using_department',none) is not none %}
    select 'using_department is still in dbt_project.yml' as error
{% else %}
    select 'none' as error_message where false
{% endif %}