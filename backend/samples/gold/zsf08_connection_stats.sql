-- Gold SQL for ZSF08_CONNECTION_STATS (only ~60 of ~5,150 lines contribute to the output)
WITH params AS (
    SELECT ARRAY_CONSTRUCT() AS s_carr,
           ARRAY_CONSTRUCT() AS s_date
),
gt_flight AS (
    SELECT f.carrid, f.connid, f.fldate, f.seatsmax, f.seatsocc
    FROM sflight f
    CROSS JOIN params p
    WHERE (ARRAY_SIZE(p.s_carr) = 0 OR ARRAY_CONTAINS(f.carrid::VARIANT, p.s_carr))
      AND (ARRAY_SIZE(p.s_date) = 0 OR ARRAY_CONTAINS(f.fldate::VARIANT, p.s_date))
),
gt_conn AS (
    SELECT DISTINCT s.carrid, s.connid, s.cityfrom, s.cityto
    FROM spfli s
    WHERE EXISTS (SELECT 1 FROM gt_flight f WHERE f.carrid = s.carrid AND f.connid = s.connid)
),
gt_stat AS (
    SELECT carrid, connid,
           COUNT(*)      AS flights,
           SUM(seatsmax) AS seatsmax,
           SUM(seatsocc) AS seatsocc
    FROM gt_flight
    GROUP BY carrid, connid
),
gt_out AS (
    SELECT st.carrid,
           COALESCE(sc.carrname, '') AS carrname,
           st.connid,
           COALESCE(c.cityfrom, '')  AS cityfrom,
           COALESCE(c.cityto, '')    AS cityto,
           st.flights, st.seatsmax, st.seatsocc
    FROM gt_stat st
    LEFT JOIN gt_conn c ON c.carrid = st.carrid AND c.connid = st.connid
    LEFT JOIN scarr sc  ON sc.carrid = st.carrid
)
SELECT carrid, carrname, connid, cityfrom, cityto, flights, seatsmax, seatsocc
FROM gt_out
ORDER BY carrid, connid;
