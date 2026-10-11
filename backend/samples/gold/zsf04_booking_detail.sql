-- Gold SQL for ZSF04_BOOKING_DETAIL
WITH params AS (
    SELECT ARRAY_CONSTRUCT() AS s_carr,
           ARRAY_CONSTRUCT() AS s_date,
           ''::VARCHAR       AS p_smok   -- checkbox, default space
),
gt_book AS (
    SELECT b.carrid, b.connid, b.fldate, b.bookid, b.customid, b.class, b.smoker, b.loccuram, b.loccurkey
    FROM sbook b
    CROSS JOIN params p
    WHERE (ARRAY_SIZE(p.s_carr) = 0 OR ARRAY_CONTAINS(b.carrid::VARIANT, p.s_carr))
      AND (ARRAY_SIZE(p.s_date) = 0 OR ARRAY_CONTAINS(b.fldate::VARIANT, p.s_date))
      AND COALESCE(TRIM(b.cancelled), '') = ''
      -- IF p_smok = 'X'. DELETE gt_book WHERE smoker <> 'X'.
      AND NOT (p.p_smok = 'X' AND COALESCE(b.smoker, '') <> 'X')
),
gt_cust AS (
    SELECT DISTINCT c.id, c.name, c.city, c.country
    FROM scustom c
    WHERE EXISTS (SELECT 1 FROM gt_book b WHERE b.customid = c.id)
),
gt_out AS (
    SELECT b.carrid, b.connid, b.fldate, b.bookid, b.customid,
           COALESCE(c.name, '') AS cust_name,
           COALESCE(c.city, '') AS cust_city,
           CASE b.class WHEN 'F' THEN 'First'
                        WHEN 'C' THEN 'Business'
                        WHEN 'Y' THEN 'Economy'
                        ELSE 'Unknown' END AS class_text,
           CASE WHEN b.smoker = 'X' THEN 'Yes' ELSE 'No' END AS smoker_txt,
           b.loccuram, b.loccurkey
    FROM gt_book b
    LEFT JOIN gt_cust c ON c.id = b.customid
)
SELECT carrid, connid, fldate, bookid, customid, cust_name, cust_city, class_text, smoker_txt, loccuram, loccurkey
FROM gt_out
ORDER BY carrid, connid, fldate, bookid;
