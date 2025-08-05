-- Define columns to compare
{% set table_name = 'obt_product_inventory' %}

{% set cols_to_compare = [
    'product_id',
    'product_code',
    'product_name',
    'description',
    'supplier_company',
    'standard_cost',
    'list_price',
    'reorder_level',
    'target_level',
    'quantity_per_unit',
    'discontinued',
    'minimum_reorder_quantity',
    'category',
    'inventory_id',
    'transaction_type',
    'transaction_created_date',
    'transaction_modified_date',
    'ipd',
    'quantity',
    'purchase_order_id',
    'customer_order_id',
    'comments'
] %}



-------------------------------------
---- DO NOT EDIT BELOW THIS LINE ----
{% set answer_key = 'solution__' + table_name %}

-- depends_on: {{ ref(answer_key) }}
-- depends_on: {{ ref(table_name) }}

{% set table_a = adapter.get_relation(database=target.database, schema=target.schema, identifier=answer_key) %}
{% set table_b = adapter.get_relation(database=target.database, schema=target.schema, identifier=table_name) %}

{% if table_a is none or table_b is none %}
    select 1
{% else %}    
    {{ dbt_utils.test_equality(
        model=ref(answer_key),
        compare_model=ref(table_name),
        compare_columns=cols_to_compare
    ) }}
{% endif %}