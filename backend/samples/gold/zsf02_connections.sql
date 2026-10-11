-- Gold SQL for ZSF02_CONNECTIONS
-- Output columns follow the ALV field catalog (FLTIME not in catalog, AIRPFROM is NO_OUT).
WITH params AS (
    SELECT ARRAY_CONSTRUCT() AS s_carr,
           ARRAY_CONSTRUCT() AS s_ctry
),
gt_conn AS (
    SELECT p.carrid, c.carrname, p.connid, p.cityfrom, p.cityto,
           p.distance, p.distid, p.fltime, p.airpfrom
    FROM spfli p
    INNER JOIN scarr c ON c.carrid = p.carrid
    CROSS JOIN params prm
    WHERE (ARRAY_SIZE(prm.s_carr) = 0 OR ARRAY_CONTAINS(p.carrid::VARIANT, prm.s_carr))
      AND (ARRAY_SIZE(prm.s_ctry) = 0 OR ARRAY_CONTAINS(p.countryfr::VARIANT, prm.s_ctry))
      AND p.distance > 0
)
SELECT carrid, carrname, connid, cityfrom, cityto, distance, distid
FROM gt_conn
ORDER BY carrid, connid;
