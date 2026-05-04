-- 1. Cleaned Data
SELECT *
FROM processed LIMIT 10;

-- 2. Total Revenue by Region
SELECT region, ROUND(SUM(revenue), 2) AS total_revenue
FROM processed
GROUP BY region
ORDER BY total_revenue DESC;

-- 3. Order Count by Status
SELECT status, COUNT(*) AS order_count
FROM processed
GROUP BY status
ORDER BY order_count DESC;

-- 4. Top 5 Categories by Total Revenue
SELECT category, ROUND(SUM(order_total), 2) AS total_revenue
FROM processed
GROUP BY category
ORDER BY total_revenue DESC
LIMIT 5;

-- 5. Average Order Value by Region
SELECT region, ROUND(AVG(order_total), 2) AS avg_order_value
FROM processed
GROUP BY region
ORDER BY avg_order_value DESC;

-- 6. Records Added by processed_at timestamp (to confirm pipeline ran)
SELECT DATE(processed_at) AS run_date, COUNT(*) AS records_processed
FROM processed
GROUP BY DATE(processed_at);
