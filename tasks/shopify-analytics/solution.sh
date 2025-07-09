#!/bin/bash
# Create the product_performance model
cat > models/product_performance.sql << 'EOF'
{{
    config(
        materialized='table'
    )
}}

with order_lines as (
    select 
        product_id,
        pre_tax_price,
        quantity,
        quantity_net_refunds,
        subtotal_net_refunds,
        refunded_subtotal,
        total_discount,
        order_line_tax
    from main.shopify_order_line_data
    where product_id is not null
),

products as (
    select 
        product_id,
        title as product_title
    from main.shopify_product_data
),

product_aggregates as (
    select 
        ol.product_id,
        sum(ol.pre_tax_price) as total_sales_revenue,
        sum(ol.quantity) as total_units_sold,
        sum(ol.refunded_subtotal) as refund_amount,
        count(case when ol.refunded_subtotal > 0 then 1 end) as refund_count,
        sum(ol.total_discount) as discount_amount,
        sum(ol.order_line_tax) as tax_amount,
        sum(ol.subtotal_net_refunds) as net_revenue,
        case 
            when sum(ol.quantity) > 0 
            then sum(ol.pre_tax_price) / sum(ol.quantity) 
            else 0 
        end as avg_selling_price
    from order_lines ol
    group by ol.product_id
)

select 
    pa.product_id,
    coalesce(p.product_title, 'Unknown Product') as product_title,
    coalesce(pa.total_sales_revenue, 0) as total_sales_revenue,
    coalesce(pa.total_units_sold, 0) as total_units_sold,
    coalesce(pa.refund_amount, 0) as refund_amount,
    coalesce(pa.refund_count, 0) as refund_count,
    coalesce(pa.discount_amount, 0) as discount_amount,
    coalesce(pa.tax_amount, 0) as tax_amount,
    coalesce(pa.net_revenue, 0) as net_revenue,
    round(coalesce(pa.avg_selling_price, 0), 2) as avg_selling_price
from product_aggregates pa
left join products p on pa.product_id = p.product_id
order by pa.total_sales_revenue desc
EOF

# Create the daily_shop_performance model
cat > models/daily_shop_performance.sql << 'EOF'
{{
    config(
        materialized='table'
    )
}}

with orders as (
    select 
        order_id,
        created_at::date as date,
        total_price,
        financial_status,
        fulfillment_status,
        subtotal_price
    from main.shopify_order_data
    where canceled_at is null
),

abandoned_checkouts as (
    select 
        created_at::date as date,
        count(*) as abandoned_count,
        sum(total_price) as abandoned_value
    from main.shopify_abandoned_checkout_data
    where completed_at is null
    group by 1
),

daily_orders as (
    select 
        date,
        count(distinct order_id) as total_orders,
        sum(total_price) as total_order_revenue,
        count(case when fulfillment_status = 'fulfilled' then 1 end) as fulfilled_orders,
        count(case when fulfillment_status is null or fulfillment_status = 'null' then 1 end) as unfulfilled_orders,
        count(case when fulfillment_status = 'partial' then 1 end) as partially_fulfilled_orders,
        avg(total_price) as avg_order_value
    from orders
    group by date
)

select 
    coalesce(o.date, ac.date) as date,
    coalesce(o.total_orders, 0) as total_orders,
    round(coalesce(o.total_order_revenue, 0), 2) as total_order_revenue,
    coalesce(ac.abandoned_count, 0) as abandoned_checkouts_count,
    round(coalesce(ac.abandoned_value, 0), 2) as abandoned_checkouts_value,
    coalesce(o.fulfilled_orders, 0) as fulfilled_orders,
    coalesce(o.unfulfilled_orders, 0) as unfulfilled_orders,
    coalesce(o.partially_fulfilled_orders, 0) as partially_fulfilled_orders,
    round(coalesce(o.avg_order_value, 0), 2) as avg_order_value
from daily_orders o
full outer join abandoned_checkouts ac on o.date = ac.date
where coalesce(o.date, ac.date) is not null
order by date desc
EOF

dbt deps

# Run dbt to create the models
dbt run --select product_performance daily_shop_performance
