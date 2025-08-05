#!/bin/bash
cat > models/intercom__threads.sql << 'EOF'
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
    count(latest_conversation_part.conversation_part_id) as total_conversation_parts,
    min(case when latest_conversation_part.part_type = 'comment' and latest_conversation_part.author_type in ('lead','user') then latest_conversation_part.created_at else null end) as first_contact_reply_at,
    min(case when latest_conversation_part.part_type like '%assignment%' then latest_conversation_part.created_at else null end) as first_assignment_at,
    min(case when latest_conversation_part.part_type in ('comment','assignment') and latest_conversation_part.author_type = 'admin' and latest_conversation_part.body is not null then latest_conversation_part.created_at else null end) as first_admin_response_at,
    min(case when latest_conversation_part.part_type = 'open' then latest_conversation_part.created_at else null end) as first_reopen_at,
    max(case when latest_conversation_part.part_type like '%assignment%' then latest_conversation_part.created_at else null end) as last_assignment_at,
    max(case when latest_conversation_part.part_type = 'comment' and latest_conversation_part.author_type in ('lead','user') then latest_conversation_part.created_at else null end) as last_contact_reply_at,
    max(case when latest_conversation_part.part_type in ('comment','assignment') and latest_conversation_part.author_type = 'admin' and latest_conversation_part.body is not null then latest_conversation_part.created_at else null end) as last_admin_response_at,
    max(case when latest_conversation_part.part_type = 'open' then latest_conversation_part.created_at else null end) as last_reopen_at,
    sum(case when latest_conversation_part.part_type like '%assignment%' then 1 else 0 end) as total_assignments,
    sum(case when latest_conversation_part.part_type = 'open' then 1 else 0 end) as total_reopens
  from latest_conversation

  left join latest_conversation_part
    on latest_conversation.conversation_id = latest_conversation_part.conversation_id

  group by 1, 2
  
)

select * 
from final
EOF

cat > models/intercom__conversation_metrics.sql << 'EOF'
with threads as (
  select *
  from {{ ref('intercom__threads') }}
),

-- Get the first and last close events for each conversation
close_events as (
  select 
    distinct conversation_id,
    first_value(created_at) over (partition by conversation_id order by created_at asc, conversation_id rows unbounded preceding) as first_close_at,
    first_value(created_at) over (partition by conversation_id order by created_at desc, conversation_id rows unbounded preceding) as last_close_at
  from {{ var('conversation_part_history') }}
  where part_type = 'close'
),

final as (
  select 
    t.conversation_id,
    t.conversation_created_at,
    t.total_reopens,
    t.total_conversation_parts,
    t.total_assignments,
    t.first_contact_reply_at,
    t.first_assignment_at,
    t.first_admin_response_at,
    t.first_reopen_at,
    t.last_assignment_at,
    t.last_contact_reply_at,
    t.last_admin_response_at,
    t.last_reopen_at,

    c.first_close_at,
    c.last_close_at,

    round(cast(({{ dbt.datediff("t.conversation_created_at", "t.first_assignment_at", 'second') }}/60) as numeric), 2) as time_to_first_assignment_minutes,
    round(cast(({{ dbt.datediff("t.conversation_created_at", "t.first_admin_response_at", 'second') }}/60) as numeric), 2) as time_to_first_response_minutes,
    round(cast(({{ dbt.datediff("t.first_contact_reply_at", "c.first_close_at", 'second') }} /60) as numeric), 2) as time_to_first_close_minutes,
    round(cast(({{ dbt.datediff("t.first_contact_reply_at", "c.last_close_at", 'second') }} /60) as numeric), 2) as time_to_last_close_minutes
  from threads t
  
  left join close_events c
    on t.conversation_id = c.conversation_id
)

select *
from final
EOF

dbt deps

# Run dbt to create the models
dbt run --select intercom__threads intercom__conversation_metrics
