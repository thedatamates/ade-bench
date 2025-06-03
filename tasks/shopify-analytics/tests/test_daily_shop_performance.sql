-- Test daily shop performance for the most recent 7 days
SELECT 
    date,
    total_orders,
    total_order_revenue,
    abandoned_checkouts_count,
    abandoned_checkouts_value,
    fulfilled_orders,
    unfulfilled_orders,
    partially_fulfilled_orders,
    avg_order_value
FROM daily_shop_performance
ORDER BY date DESC
LIMIT 7;