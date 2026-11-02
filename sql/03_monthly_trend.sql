-- Dialect: SQLite 3.25+ (window functions). Grain: source booking row.
WITH m AS (SELECT month,COUNT(*) bookings,SUM(is_completed) completed,SUM(completed_value) completed_value,
 ROUND(100.0*SUM(is_completed)/COUNT(*),2) completion_pct FROM bookings GROUP BY month)
 SELECT *, ROUND(100.0*(bookings-LAG(bookings) OVER(ORDER BY month))/NULLIF(LAG(bookings) OVER(ORDER BY month),0),2) mom_bookings_pct FROM m ORDER BY month;
