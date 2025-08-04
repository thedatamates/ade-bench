-- Helper macro to select columns from a table
{% macro foo() %}
  select 1
{% endmacro %}


{{ foo() }}