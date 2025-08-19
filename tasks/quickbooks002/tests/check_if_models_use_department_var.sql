{% set tables = [
    "int_quickbooks__expenses_union",
    "int_quickbooks__sales_union",
    "quickbooks__ap_ar_enhanced"
] %}

{% for table_name in tables %}
    {% set node = graph.nodes["model." ~ project_name ~ "." ~ table_name ] %}
    {% set raw_sql = node.raw_code | lower %}
    
    {% if "using_department" in raw_sql %}
        -- Model should not old variable
        select 'using_department is in {{ table_name }} should not be' as error_message union all
    {% endif %}

{% endfor %}
    
    select 'none' as error_message where false