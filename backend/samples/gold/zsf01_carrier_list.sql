-- Gold SQL for ZSF01_CARRIER_LIST
WITH params AS (
    SELECT 'EUR'::VARCHAR      AS p_curr,   -- PARAMETERS p_curr DEFAULT 'EUR'
           ARRAY_CONSTRUCT()   AS s_carr    -- SELECT-OPTIONS s_carr (empty = all)
),
gt_carrier AS (
    SELECT c.carrid, c.carrname, c.currcode, c.url
    FROM scarr c
    CROSS JOIN params p
    WHERE (ARRAY_SIZE(p.s_carr) = 0 OR ARRAY_CONTAINS(c.carrid::VARIANT, p.s_carr))
      AND c.currcode = p.p_curr
)
SELECT carrid, carrname, currcode, url
FROM gt_carrier
ORDER BY carrid;
