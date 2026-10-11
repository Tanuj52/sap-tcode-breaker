-- Gold SQL for ZSF06_PEAK_FLIGHTS
WITH params AS (
    SELECT ARRAY_CONSTRUCT() AS s_carr,
           1                 AS p_minocc
),
gt_flight_read AS (
    SELECT f.carrid, f.connid, f.fldate, f.planetype, f.seatsmax, f.seatsocc
    FROM sflight f
    CROSS JOIN params p
    WHERE (ARRAY_SIZE(p.s_carr) = 0 OR ARRAY_CONTAINS(f.carrid::VARIANT, p.s_carr))
),
-- DELETE gt_flight WHERE seatsocc < p_minocc
gt_flight_min AS (
    SELECT f.*
    FROM gt_flight_read f
    CROSS JOIN params p
    WHERE NOT (f.seatsocc < p.p_minocc)
),
-- SORT BY carrid connid seatsocc DESCENDING fldate + DELETE ADJACENT DUPLICATES COMPARING carrid connid
gt_flight_peak AS (
    SELECT *
    FROM gt_flight_min
    QUALIFY ROW_NUMBER() OVER (PARTITION BY carrid, connid ORDER BY seatsocc DESC, fldate ASC) = 1
),
gt_flight AS (
    SELECT carrid, connid, fldate, planetype, seatsmax, seatsocc,
           CASE WHEN seatsocc >= seatsmax     THEN 'FULL'
                WHEN seatsocc * 2 >= seatsmax THEN 'HIGH'
                ELSE 'LOW' END AS band
    FROM gt_flight_peak
)
SELECT carrid, connid, fldate, planetype, seatsmax, seatsocc, band
FROM gt_flight
ORDER BY carrid, connid;
