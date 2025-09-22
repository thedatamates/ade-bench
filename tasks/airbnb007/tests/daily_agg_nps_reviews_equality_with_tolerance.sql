{% set test_and_solution_tables = ['daily_agg_nps_reviews','solution__daily_agg_nps_reviews'] %}

{% set date_cols = ['review_date'] %}
{% set numeric_cols = ['nps_daily', 'reviews_daily', 'nps_28d', 'reviews_28d'] %}
{% set sum_tolerance = 0.01 %}
{% set avg_tolerance = 0.01 %}

-------------------------------------
--- DO NOT EDIT BELOW THIS LINE ----
-------------------------------------

{% set all_cols = date_cols + numeric_cols %}

with
{% for tbl in test_and_solution_tables %}
cte_{{tbl}} as (
  select
    {% for d in date_cols %}
      min({{ d }}) as agg_1_{{ d }},
      max({{ d }}) as agg_2_{{ d }},
    {% endfor %}

    {% for n in numeric_cols %}
      sum({{ n }}) as agg_1_{{ n }},
      avg({{ n }}) as agg_2_{{ n }},
    {% endfor %}

      count(*) as total_rows

  from {{ tbl }}
),
{% endfor %}

combined as (
  {% for c in all_cols %}
    select
      '{{ c }}' as column_name,
      {% if c in date_cols %}
        'min/max' as comparison_types,
      {% else %}
        'sum/avg' as comparison_types,
      {% endif %}
      s.agg_1_{{ c }}::VARCHAR as solution_comparsion_type_1,
      t.agg_1_{{ c }}::VARCHAR as test_comparsion_type_1,
      s.agg_2_{{ c }}::VARCHAR as solution_comparsion_type_2,
      t.agg_2_{{ c }}::VARCHAR as test_comparsion_type_2,
    from cte_{{ test_and_solution_tables[0] }} s
    join cte_{{ test_and_solution_tables[1] }} t
      on 1 = 1
      {% if c in date_cols %}
        and (
             s.agg_1_{{ c }} != t.agg_1_{{ c }}
          or s.agg_2_{{ c }} != t.agg_2_{{ c }}
        )
      {% else %}
        and (
             t.agg_1_{{ c }} > s.agg_1_{{ c }} * (1 + {{ sum_tolerance }})
          or t.agg_1_{{ c }} < s.agg_1_{{ c }} * (1 - {{ sum_tolerance }})
          or t.agg_2_{{ c }} > s.agg_2_{{ c }} * (1 + {{ avg_tolerance }})
          or t.agg_2_{{ c }} < s.agg_2_{{ c }} * (1 - {{ avg_tolerance }})
        )
      {% endif %}

    union all

    {% endfor %}

    select
      'total_rows' as column_name,
      'total_rows/NA' as comparison_types,
      s.total_rows::VARCHAR as solution_comparsion_type_1,
      t.total_rows::VARCHAR as test_comparsion_type_1,
      'NA' as solution_comparsion_type_2,
      'NA' as test_comparsion_type_2,
    from cte_{{ test_and_solution_tables[0] }} s
    join cte_{{ test_and_solution_tables[1] }} t
      on 1 = 1
      and s.total_rows != t.total_rows
  )

  select * from combined