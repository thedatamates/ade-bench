-- Test product performance metrics for top 5 products by revenue
SELECT 
    product_id,
    product_title,
    total_sales_revenue,
    total_units_sold,
    refund_amount,
    refund_count,
    discount_amount,
    tax_amount,
    net_revenue,
    avg_selling_price
FROM product_performance
ORDER BY total_sales_revenue DESC
LIMIT 5;