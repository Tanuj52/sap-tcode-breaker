-- Gold SQL for ZS4_GOODS_MOVEMENTS (target: S/4HANA replica, physical MATDOC only)
-- MKPF/MSEG are compatibility views over MATDOC; header fields (BUDAT) live in MATDOC.
WITH params AS (
    SELECT ARRAY_CONSTRUCT() AS s_werks,
           ARRAY_CONSTRUCT() AS s_matnr,
           ARRAY_CONSTRUCT() AS s_budat,
           ARRAY_CONSTRUCT() AS s_bwart
),
gt_out_read AS (
    SELECT m.mblnr, m.mjahr, m.zeile, m.budat, m.matnr, m.werks,
           m.lgort, m.bwart, m.shkzg, m.menge, m.meins
    FROM matdoc m
    CROSS JOIN params p
    WHERE m.record_type = 'MDOC'
      AND (ARRAY_SIZE(p.s_werks) = 0 OR ARRAY_CONTAINS(m.werks::VARIANT, p.s_werks))
      AND (ARRAY_SIZE(p.s_matnr) = 0 OR ARRAY_CONTAINS(m.matnr::VARIANT, p.s_matnr))
      AND (ARRAY_SIZE(p.s_budat) = 0 OR ARRAY_CONTAINS(m.budat::VARIANT, p.s_budat))
      AND (ARRAY_SIZE(p.s_bwart) = 0 OR ARRAY_CONTAINS(m.bwart::VARIANT, p.s_bwart))
),
gt_makt AS (
    SELECT DISTINCT t.matnr, t.maktx
    FROM makt t
    WHERE t.spras = 'E'   -- sy-langu
      AND EXISTS (SELECT 1 FROM gt_out_read o WHERE o.matnr = t.matnr)
),
gt_out AS (
    SELECT o.mblnr, o.mjahr, o.zeile, o.budat, o.matnr,
           COALESCE(t.maktx, '') AS maktx,
           o.werks, o.lgort, o.bwart, o.shkzg, o.menge, o.meins,
           CASE WHEN o.shkzg = 'H' THEN o.menge * -1 ELSE o.menge END AS signed_qty
    FROM gt_out_read o
    LEFT JOIN gt_makt t ON t.matnr = o.matnr
)
SELECT mblnr, mjahr, zeile, budat, matnr, maktx, werks, lgort, bwart, shkzg, menge, meins, signed_qty
FROM gt_out
ORDER BY budat, mblnr, zeile;
