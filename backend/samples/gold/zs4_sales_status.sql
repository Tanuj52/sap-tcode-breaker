-- Gold SQL for ZS4_SALES_STATUS (target: S/4HANA replica, VBUK removed, GBSTK on VBAK)
WITH params AS (
    SELECT ARRAY_CONSTRUCT() AS s_vkorg,
           ARRAY_CONSTRUCT() AS s_erdat,
           'X'::VARCHAR      AS p_open
),
lt_head AS (
    SELECT h.vbeln, h.erdat, h.kunnr,
           COALESCE(c.name1, '') AS name1,
           h.netwr, h.waerk, h.gbstk
    FROM vbak h
    LEFT JOIN kna1 c ON c.kunnr = h.kunnr
    CROSS JOIN params p
    WHERE (ARRAY_SIZE(p.s_vkorg) = 0 OR ARRAY_CONTAINS(h.vkorg::VARIANT, p.s_vkorg))
      AND (ARRAY_SIZE(p.s_erdat) = 0 OR ARRAY_CONTAINS(h.erdat::VARIANT, p.s_erdat))
      -- IF p_open = abap_true. DELETE lt_head WHERE gbstk = 'C'.
      AND NOT (p.p_open = 'X' AND h.gbstk = 'C')
),
lt_items AS (
    SELECT DISTINCT i.vbeln, i.posnr
    FROM vbap i
    WHERE EXISTS (SELECT 1 FROM lt_head h WHERE h.vbeln = i.vbeln)
),
lt_out AS (
    SELECT h.vbeln, h.erdat, h.kunnr, h.name1, h.netwr, h.waerk, h.gbstk,
           CASE WHEN h.gbstk = 'A' THEN 'Open'
                WHEN h.gbstk = 'B' THEN 'In Process'
                WHEN h.gbstk = 'C' THEN 'Completed'
                ELSE 'Unknown' END AS status_txt,
           COALESCE(ic.item_count, 0) AS item_count
    FROM lt_head h
    LEFT JOIN (SELECT vbeln, COUNT(*) AS item_count FROM lt_items GROUP BY vbeln) ic
           ON ic.vbeln = h.vbeln
)
SELECT vbeln, erdat, kunnr, name1, netwr, waerk, gbstk, status_txt, item_count
FROM lt_out
ORDER BY vbeln;
