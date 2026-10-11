-- Gold SQL for ZSF09_CARRIER_TOTALS (AT END OF carrid + SUM = totals per airline)
WITH params AS (
    SELECT ARRAY_CONSTRUCT() AS s_carr
),
gt_flight AS (
    SELECT f.carrid, f.seatsmax, f.seatsocc
    FROM sflight f
    CROSS JOIN params p
    WHERE (ARRAY_SIZE(p.s_carr) = 0 OR ARRAY_CONTAINS(f.carrid::VARIANT, p.s_carr))
),
gt_out AS (
    SELECT carrid, SUM(seatsmax) AS seatsmax, SUM(seatsocc) AS seatsocc
    FROM gt_flight
    GROUP BY carrid
)
SELECT carrid, seatsmax, seatsocc FROM gt_out ORDER BY carrid;
