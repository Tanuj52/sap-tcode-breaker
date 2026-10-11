-- Gold SQL for ZSF07_CUSTOMER_TRIPS
-- Z_GET_DISCOUNT inlined from its source; standard FMs mapped from the FM catalog.
WITH params AS (
    SELECT ARRAY_CONSTRUCT() AS s_cust,
           ARRAY_CONSTRUCT() AS s_carr
),
gt_book AS (
    SELECT b.carrid, b.connid, b.fldate, b.bookid, b.customid, b.class, b.loccuram, b.loccurkey
    FROM sbook b
    CROSS JOIN params p
    WHERE (ARRAY_SIZE(p.s_cust) = 0 OR ARRAY_CONTAINS(b.customid::VARIANT, p.s_cust))
      AND (ARRAY_SIZE(p.s_carr) = 0 OR ARRAY_CONTAINS(b.carrid::VARIANT, p.s_carr))
      AND COALESCE(TRIM(b.cancelled), '') = ''
),
gt_cust AS (
    SELECT DISTINCT c.id, c.name, c.discount
    FROM scustom c
    WHERE EXISTS (SELECT 1 FROM gt_book b WHERE b.customid = c.id)
),
gt_out_base AS (
    SELECT b.customid,
           -- CONVERSION_EXIT_ALPHA_OUTPUT
           CASE WHEN TRY_TO_NUMBER(b.customid) IS NOT NULL THEN LTRIM(b.customid, '0') ELSE b.customid END AS cust_ext,
           COALESCE(c.name, '') AS cust_name,
           b.carrid, b.connid, b.fldate,
           -- DATE_COMPUTE_DAY: 1 = Monday ... 7 = Sunday
           DAYOFWEEKISO(TRY_TO_DATE(b.fldate, 'YYYYMMDD')) AS weekday,
           b.class, b.loccuram,
           -- Z_GET_DISCOUNT, only called when the customer was found
           CASE WHEN c.id IS NULL                        THEN 0
                WHEN TRY_TO_NUMBER(c.discount) > 0       THEN TRY_TO_NUMBER(c.discount)
                WHEN b.class = 'F'                       THEN 10
                WHEN b.class = 'C'                       THEN 5
                ELSE 0 END AS discount_pct,
           b.loccurkey
    FROM gt_book b
    LEFT JOIN gt_cust c ON c.id = b.customid
),
gt_out AS (
    SELECT customid, cust_ext, cust_name, carrid, connid, fldate, weekday, class, loccuram,
           discount_pct,
           ROUND(loccuram * (100 - discount_pct) / 100, 2) AS net_amount,
           loccurkey
    FROM gt_out_base
)
SELECT customid, cust_ext, cust_name, carrid, connid, fldate, weekday, class, loccuram,
       discount_pct, net_amount, loccurkey
FROM gt_out
ORDER BY customid, fldate, carrid, connid;
