#!/bin/bash

# Create the dim_products model
cat > models/warehouse/dim_products.sql << 'EOF'
WITH source AS (
    SELECT  
        p.id AS product_id,
        p.product_code,
        p.product_name,
        p.description,
        s.company AS supplier_company,
        p.standard_cost,
        p.list_price,
        p.reorder_level,
        p.target_level,
        p.quantity_per_unit,
        p.discontinued,
        p.minimum_reorder_quantity,
        p.category,
        p.attachments,
        get_current_timestamp() AS insertion_timestamp
    FROM {{ ref('stg_products') }} p
    LEFT JOIN {{ ref('stg_suppliers') }} s
    ON s.id = p.supplier_id
),

unique_source AS (
    SELECT *,
           row_number() OVER(PARTITION BY product_id ORDER BY product_id) AS row_number
    FROM source
)

SELECT
    product_id,
    product_code,
    product_name,
    description,
    supplier_company,
    standard_cost,
    list_price,
    reorder_level,
    target_level,
    quantity_per_unit,
    discontinued,
    minimum_reorder_quantity,
    category,
    attachments,
    insertion_timestamp
FROM unique_source
WHERE row_number = 1
EOF

# Create the fact_inventory model
cat > models/warehouse/fact_inventory.sql << 'EOF'
{{ config(
    partition_by={
        "field": "transaction_created_date",
        "data_type": "date"
    }
) }}

WITH source AS (
    SELECT
        id AS inventory_id,
        transaction_type,
        CAST(STRPTIME(transaction_created_date, '%m/%d/%Y %H:%M:%S') AS DATE) AS transaction_created_date,
        transaction_modified_date,
        product_id,
        quantity,
        purchase_order_id,
        customer_order_id,
        comments,
        get_current_timestamp() AS insertion_timestamp
    FROM {{ ref('stg_inventory_transactions') }}
),

unique_source AS (
    SELECT
        *,
        ROW_NUMBER() OVER(PARTITION BY inventory_id ORDER BY inventory_id) AS row_number
    FROM source
)

SELECT
    inventory_id,
    transaction_type,
    transaction_created_date,
    transaction_modified_date,
    product_id,
    quantity,
    purchase_order_id,
    customer_order_id,
    comments,
    insertion_timestamp
FROM unique_source
WHERE row_number = 1
EOF

# Create the obt_product_inventory model
cat > models/analytics_obt/obt_product_inventory.sql << 'EOF'
WITH source AS (
    SELECT
        p.product_id,
        p.product_code,
        p.product_name,
        p.description,
        p.supplier_company,
        p.standard_cost,
        p.list_price,
        p.reorder_level,
        p.target_level,
        p.quantity_per_unit,
        p.discontinued,
        p.minimum_reorder_quantity,
        p.category,
        i.inventory_id,
        i.transaction_type,
        i.transaction_created_date,
        i.transaction_modified_date,
        i.product_id AS ipd,
        i.quantity,
        i.purchase_order_id,
        i.customer_order_id,
        i.comments,
        get_current_timestamp() AS insertion_timestamp,
FROM {{ ref('fact_inventory') }} i
LEFT JOIN {{ ref('dim_products') }} p
ON p.product_id = i.product_id
)

SELECT *
FROM source
EOF

# Run dbt to create the models
dbt run --select dim_products fact_inventory obt_product_inventory 
