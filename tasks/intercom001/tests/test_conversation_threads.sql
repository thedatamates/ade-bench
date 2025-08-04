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
{% macro select_columns(table, columns) %}
    select 
        {% for col in columns %}
            {{ col }}{% if not loop.last %}, {% endif %}
        {% endfor %}
    from {{ table }}
{% endmacro %}

-- Macro to compare two tables
{% macro compare_tables(table_a, table_b, columns) %}
    a as ({{ select_columns(table_a, columns) }}),
    b as ({{ select_columns(table_b, columns) }}),
    c as (select * from a union select * from b),

    a_count as (select count(*) as row_count from a),
    b_count as (select count(*) as row_count from b),
    c_count as (select count(*) as row_count from c)

    select a_count.row_count, b_count.row_count, c_count.row_count
    from a_count
    join b_count on 1 = 1
    join c_count on 1 = 1
    where a_count.row_count != b_count.row_count
        or a_count.row_count != c_count.row_count
        or b_count.row_count != c_count.row_count

{% endmacro %}

-- Create the solution table
with latest_conversation_part as (
  select *
  from {{ var('conversation_part_history') }}
  where coalesce(_fivetran_active, true)
),

latest_conversation as (
  select *
  from {{ var('conversation_history') }}
  where coalesce(_fivetran_active, true)
),

--Aggregates conversation part data related to a single conversation from the int_intercom__latest_conversation model. See below for specific aggregates.
final as (
  select 
    latest_conversation.conversation_id,
    latest_conversation.created_at as conversation_created_at,
    count(latest_conversation_part.conversation_part_id) as count_total_parts,
    min(case when latest_conversation_part.part_type = 'comment' and latest_conversation_part.author_type in ('lead','user') then latest_conversation_part.created_at else null end) as first_contact_reply_at,
    min(case when latest_conversation_part.part_type like '%assignment%' then latest_conversation_part.created_at else null end) as first_assignment_at,
    min(case when latest_conversation_part.part_type in ('comment','assignment') and latest_conversation_part.author_type = 'admin' and latest_conversation_part.body is not null then latest_conversation_part.created_at else null end) as first_admin_response_at,
    min(case when latest_conversation_part.part_type = 'open' then latest_conversation_part.created_at else null end) as first_reopen_at,
    max(case when latest_conversation_part.part_type like '%assignment%' then latest_conversation_part.created_at else null end) as last_assignment_at,
    max(case when latest_conversation_part.part_type = 'comment' and latest_conversation_part.author_type in ('lead','user') then latest_conversation_part.created_at else null end) as last_contact_reply_at,
    max(case when latest_conversation_part.part_type in ('comment','assignment') and latest_conversation_part.author_type = 'admin' and latest_conversation_part.body is not null then latest_conversation_part.created_at else null end) as last_admin_response_at,
    max(case when latest_conversation_part.part_type = 'open' then latest_conversation_part.created_at else null end) as last_reopen_at,
    sum(case when latest_conversation_part.part_type like '%assignment%' then 1 else 0 end) as count_assignments,
    sum(case when latest_conversation_part.part_type = 'open' then 1 else 0 end) as count_reopens
  from latest_conversation

  left join latest_conversation_part
    on latest_conversation.conversation_id = latest_conversation_part.conversation_id

  group by 1, 2
),

{{ compare_tables('final', 'intercom__threads', cols_to_compare) }}