-- Gold SQL for ZSF05_MONTHLY_REVENUE
WITH params AS (
    SELECT ARRAY_CONSTRUCT() AS s_carr,
           ARRAY_CONSTRUCT() AS s_date
),
gt_book AS (
    SELECT b.carrid, b.fldate, b.loccuram, b.loccurkey
    FROM sbook b
    CROSS JOIN params p
    WHERE (ARRAY_SIZE(p.s_carr) = 0 OR ARRAY_CONTAINS(b.carrid::VARIANT, p.s_carr))
      AND (ARRAY_SIZE(p.s_date) = 0 OR ARRAY_CONTAINS(b.fldate::VARIANT, p.s_date))
      AND COALESCE(b.cancelled, '') <> 'X'
),
-- COLLECT: key = character-like fields, numeric fields are summed
gt_sum AS (
    SELECT carrid,
           SUBSTR(fldate, 1, 6) AS month,
           loccurkey,
           COUNT(*)             AS bookings,
           SUM(loccuram)        AS revenue
    FROM gt_book
    GROUP BY carrid, SUBSTR(fldate, 1, 6), loccurkey
),
gt_out AS (
    SELECT s.carrid,
           COALESCE(c.carrname, '') AS carrname,   -- SELECT SINGLE in loop, lv_name cleared
           s.month, s.loccurkey, s.bookings, s.revenue,
           CASE WHEN s.bookings > 0 THEN ROUND(s.revenue / s.bookings, 2) ELSE 0 END AS avg_rev
    FROM gt_sum s
    LEFT JOIN scarr c ON c.carrid = s.carrid
)
SELECT carrid, carrname, month, loccurkey, bookings, revenue, avg_rev
FROM gt_out
ORDER BY carrid, month;
