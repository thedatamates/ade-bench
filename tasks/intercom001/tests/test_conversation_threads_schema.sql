-- Define columns to compare
{% set cols_to_compare = [
    'conversation_id',
    'conversation_created_at',
    'total_conversation_parts',
    'first_contact_reply_at',
    'first_assignment_at',
    'first_admin_response_at',
    'first_reopen_at',
    'last_assignment_at',
    'last_contact_reply_at',
    'total_assignments',
    'total_reopens'
] %}

-- Helper macro to select columns from a table
{% macro check_schema(table, columns) %}

  {% set num_cols = columns | length %}

  with matches as (
    select count(*) as row_count
    from "information_schema"."columns"
    where table_catalog not in ('temp','localmemdb','_duckdb_ui')
      and table_name = '{{ table }}'
      and column_name in (
        {% for col in columns %}
          '{{ col }}'{% if not loop.last %}, {% endif %}
        {% endfor %}
      )
  )

  select * from matches where row_count != {{ num_cols }}
{% endmacro %}

{{ check_schema('intercom__threads', cols_to_compare) }}