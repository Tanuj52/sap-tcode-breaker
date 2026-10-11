-- Gold SQL for ZSF03_FLIGHT_OCCUPANCY
WITH params AS (
    SELECT ARRAY_CONSTRUCT() AS s_carr,
           ARRAY_CONSTRUCT() AS s_date
),
gt_spfli AS (
    SELECT s.carrid, s.connid, s.cityfrom, s.cityto
    FROM spfli s
    CROSS JOIN params p
    WHERE (ARRAY_SIZE(p.s_carr) = 0 OR ARRAY_CONTAINS(s.carrid::VARIANT, p.s_carr))
),
-- FOR ALL ENTRIES IN gt_spfli: semi-join, result set is de-duplicated
gt_flight AS (
    SELECT DISTINCT f.carrid, f.connid, f.fldate, f.price, f.currency, f.seatsmax, f.seatsocc
    FROM sflight f
    CROSS JOIN params p
    WHERE EXISTS (SELECT 1 FROM gt_spfli s WHERE s.carrid = f.carrid AND s.connid = f.connid)
      AND (ARRAY_SIZE(p.s_date) = 0 OR ARRAY_CONTAINS(f.fldate::VARIANT, p.s_date))
),
gt_out AS (
    SELECT f.carrid, f.connid,
           COALESCE(s.cityfrom, '') AS cityfrom,
           COALESCE(s.cityto, '')   AS cityto,
           f.fldate, f.price, f.currency, f.seatsmax, f.seatsocc,
           f.seatsmax - f.seatsocc  AS seatsfree,
           CASE WHEN f.seatsmax > 0 THEN ROUND(f.seatsocc * 100 / f.seatsmax, 2) ELSE 0 END AS occ_pct
    FROM gt_flight f
    LEFT JOIN gt_spfli s ON s.carrid = f.carrid AND s.connid = f.connid
)
SELECT carrid, connid, cityfrom, cityto, fldate, price, currency, seatsmax, seatsocc, seatsfree, occ_pct
FROM gt_out
ORDER BY carrid, connid, fldate;
