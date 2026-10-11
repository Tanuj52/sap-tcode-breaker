"""Deterministic synthetic SAP demo data for the bundled samples.

Designed around edge cases that distinguish correct from almost-correct SQL:
LEFT JOIN misses, cancelled rows, zero divisors, ties in top-1-per-group,
inner-join drops, language filters and S/4 record-type filters.
"""

from __future__ import annotations

import random
from decimal import Decimal

from ..knowledge.kb import KnowledgeBase
from ..validate.stubs import ddl_for_table

DEMO_TABLES = ["SCARR", "SPFLI", "SFLIGHT", "SBOOK", "SCUSTOM", "VBAK", "VBAP", "KNA1", "MATDOC", "MAKT", "TCURX"]

_CARRIERS = [
    ("AA", "American Airlines", "USD", "http://www.aa.com"),
    ("LH", "Lufthansa", "EUR", "http://www.lufthansa.com"),
    ("AF", "Air France", "EUR", "http://www.airfrance.fr"),
    ("BA", "British Airways", "GBP", "http://www.british-airways.com"),
    ("JL", "Japan Airlines", "JPY", "http://www.jal.co.jp"),
    ("SQ", "Singapore Airlines", "SGD", "http://www.singaporeair.com"),
    ("UA", "United Airlines", "USD", "http://www.ual.com"),
    ("AZ", "Alitalia", "EUR", "http://www.alitalia.it"),
]

_CITIES = [
    ("DE", "FRANKFURT", "FRA"), ("DE", "BERLIN", "TXL"), ("US", "NEW YORK", "JFK"), ("US", "SAN FRANCISCO", "SFO"),
    ("FR", "PARIS", "CDG"), ("GB", "LONDON", "LHR"), ("JP", "TOKYO", "HND"), ("SG", "SINGAPORE", "SIN"),
    ("IT", "ROME", "FCO"), ("US", "CHICAGO", "ORD"),
]


def _rows() -> dict[str, tuple[list[str], list[tuple]]]:
    rnd = random.Random(20261009)
    data: dict[str, tuple[list[str], list[tuple]]] = {}

    data["SCARR"] = (["MANDT", "CARRID", "CARRNAME", "CURRCODE", "URL"], [("100", *c) for c in _CARRIERS])

    spfli_cols = ["MANDT", "CARRID", "CONNID", "COUNTRYFR", "CITYFROM", "AIRPFROM", "COUNTRYTO", "CITYTO", "AIRPTO",
                  "FLTIME", "DEPTIME", "ARRTIME", "DISTANCE", "DISTID", "FLTYPE", "PERIOD"]
    spfli = []
    connections = []
    for ci, (carrid, *_rest) in enumerate(_CARRIERS):
        for k in range(3):
            connid = f"{(ci + 1) * 100 + k * 7 + 1:04d}"
            a, b = rnd.sample(_CITIES, 2)
            distance = Decimal(rnd.randint(300, 9000)) if not (carrid == "AZ" and k == 2) else Decimal(0)
            spfli.append(("100", carrid, connid, a[0], a[1], a[2], b[0], b[1], b[2], rnd.randint(60, 720),
                          f"{rnd.randint(5, 22):02d}{rnd.choice(['00', '15', '30', '45'])}00", "000000",
                          distance, rnd.choice(["KM", "MI"]), "", 0))
            connections.append((carrid, connid))
    # connection of a carrier that does not exist in SCARR (dropped by INNER JOIN)
    spfli.append(("100", "ZZ", "0999", "DE", "BERLIN", "TXL", "FR", "PARIS", "CDG", 95, "080000", "093500",
                  Decimal(870), "KM", "", 0))
    connections.append(("ZZ", "0999"))
    data["SPFLI"] = (spfli_cols, spfli)

    sflight_cols = ["MANDT", "CARRID", "CONNID", "FLDATE", "PRICE", "CURRENCY", "PLANETYPE", "SEATSMAX", "SEATSOCC",
                    "PAYMENTSUM", "SEATSMAX_B", "SEATSOCC_B", "SEATSMAX_F", "SEATSOCC_F"]
    currency = {c[0]: c[2] for c in _CARRIERS} | {"ZZ": "EUR"}
    sflight = []
    flights = []
    for idx, (carrid, connid) in enumerate(connections):
        tie_occ = None
        for m in range(1, 9):
            fldate = f"2026{m:02d}{rnd.randint(1, 28):02d}"
            seatsmax = rnd.choice([180, 220, 280, 385])
            if idx == 0 and m == 1:
                seatsmax = 0  # zero divisor
            occ = rnd.randint(0, seatsmax) if seatsmax else 0
            if idx % 4 == 1 and m in (3, 6):  # tie for the peak flight
                tie_occ = tie_occ or seatsmax
                occ = seatsmax = tie_occ
            if idx % 5 == 2 and m == 4:
                occ = seatsmax  # full flight
            price = Decimal(rnd.randint(9000, 120000)) / 100
            sflight.append(("100", carrid, connid, fldate, price, currency[carrid], rnd.choice(["A320", "A380", "747-400", "767-200"]),
                            seatsmax, occ, price * occ, 30, rnd.randint(0, 30), 10, rnd.randint(0, 10)))
            flights.append((carrid, connid, fldate))
    # flights whose connection is missing from SPFLI (empty city after READ TABLE)
    for m in (2, 5):
        fldate = f"2026{m:02d}15"
        sflight.append(("100", "LH", "9999", fldate, Decimal("450.00"), "EUR", "A320", 180, 90, Decimal("40500.00"), 0, 0, 0, 0))
        flights.append(("LH", "9999", fldate))
    data["SFLIGHT"] = (sflight_cols, sflight)

    scustom_cols = ["MANDT", "ID", "NAME", "FORM", "STREET", "POSTBOX", "POSTCODE", "CITY", "COUNTRY", "REGION",
                    "TELEPHONE", "CUSTTYPE", "DISCOUNT", "LANGU", "EMAIL", "WEBUSER"]
    first = ["Anna", "Ben", "Chen", "Dana", "Eli", "Fatima", "Goro", "Hana", "Ivan", "Jia", "Kofi", "Lena"]
    last = ["Schmidt", "Miller", "Tanaka", "Rossi", "Dubois", "Kumar", "Nguyen", "Smith", "Silva", "Novak"]
    scustom = []
    for i in range(1, 121):
        city = rnd.choice(_CITIES)
        scustom.append(("100", f"{i:08d}", f"{rnd.choice(first)} {rnd.choice(last)}", rnd.choice(["Mr.", "Ms."]),
                        f"{rnd.randint(1, 200)} Main St", "", f"{rnd.randint(10000, 99999)}", city[1], city[0], "",
                        "", rnd.choice(["P", "B"]), rnd.choice(["000", "000", "000", "005", "015"]), "E", "", ""))
    data["SCUSTOM"] = (scustom_cols, scustom)

    sbook_cols = ["MANDT", "CARRID", "CONNID", "FLDATE", "BOOKID", "CUSTOMID", "CUSTTYPE", "SMOKER", "LUGGWEIGHT", "WUNIT",
                  "INVOICE", "CLASS", "FORCURAM", "FORCURKEY", "LOCCURAM", "LOCCURKEY", "ORDER_DATE", "COUNTER",
                  "AGENCYNUM", "CANCELLED", "RESERVED", "PASSNAME", "PASSFORM", "PASSBIRTH"]
    sbook = []
    bookid = 0
    for carrid, connid, fldate in flights:
        for _ in range(rnd.randint(3, 12)):
            bookid += 1
            cust = rnd.randint(1, 125)  # 121..125 do not exist in SCUSTOM
            cls = rnd.choice(["Y", "Y", "Y", "C", "F", " "])
            amount = Decimal(rnd.randint(5000, 250000)) / 100
            sbook.append(("100", carrid, connid, fldate, f"{bookid:08d}", f"{cust:08d}", "P", rnd.choice(["X", "", ""]),
                          Decimal(rnd.randint(0, 30)), "KG", "", cls.strip(), amount, currency[carrid], amount,
                          currency[carrid], "20251201", "00000001", "00000100",
                          "X" if rnd.random() < 0.1 else "", "", "", "", "19800101"))
    data["SBOOK"] = (sbook_cols, sbook)

    data["TCURX"] = (["CURRKEY", "CURRDEC"], [("JPY", 0), ("KRW", 0), ("KWD", 3)])

    kna1_cols = ["MANDT", "KUNNR", "LAND1", "NAME1", "NAME2", "ORT01", "PSTLZ", "REGIO", "STRAS", "KTOKD", "LOEVM", "STCD1"]
    kna1 = [("100", f"{1000 + i:010d}", "DE", f"Customer {i:02d} GmbH", "", "Berlin", "10115", "", "Hauptstr. 1", "KUNA", "", "")
            for i in range(1, 21)]
    data["KNA1"] = (kna1_cols, kna1)

    vbak_cols = ["MANDT", "VBELN", "ERDAT", "ERZET", "ERNAM", "AUDAT", "VBTYP", "AUART", "NETWR", "WAERK", "VKORG",
                 "VTWEG", "SPART", "VKBUR", "KUNNR", "BSTNK", "GBSTK", "ABSTK", "LFSTK", "FKSTK"]
    vbap_cols = ["MANDT", "VBELN", "POSNR", "MATNR", "ARKTX", "PSTYV", "ABGRU", "KWMENG", "VRKME", "NETWR", "WAERK",
                 "WERKS", "LGORT", "ERDAT", "GBSTA", "LFSTA"]
    vbak, vbap = [], []
    for i in range(1, 61):
        vbeln = f"{10000000 + i:010d}"
        erdat = f"2026{rnd.randint(1, 9):02d}{rnd.randint(1, 28):02d}"
        kunnr = f"{1000 + rnd.randint(1, 24):010d}"  # 21..24 missing in KNA1
        gbstk = rnd.choice(["A", "B", "C", "C", ""])
        vbak.append(("100", vbeln, erdat, "101500", "SALES01", erdat, "C", "OR", Decimal(rnd.randint(1000, 900000)) / 100,
                     "EUR", rnd.choice(["1000", "2000"]), "10", "00", "", kunnr, f"PO-{i}", gbstk, "", "", ""))
        for p in range(rnd.randint(0, 4)):
            vbap.append(("100", vbeln, f"{(p + 1) * 10:06d}", f"MAT-{rnd.randint(1, 30):03d}", "Item", "TAN", "",
                         Decimal(rnd.randint(1, 50)), "EA", Decimal(rnd.randint(100, 50000)) / 100, "EUR", "1000", "0001",
                         erdat, gbstk, ""))
    data["VBAK"] = (vbak_cols, vbak)
    data["VBAP"] = (vbap_cols, vbap)

    makt_cols = ["MANDT", "MATNR", "SPRAS", "MAKTX", "MAKTG"]
    makt = []
    for m in range(1, 31):
        matnr = f"{m:018d}"
        if m % 7 == 0:
            continue  # no description at all
        if m % 5 == 0:
            makt.append(("100", matnr, "D", f"Material {m} (DE)", f"MATERIAL {m} (DE)"))  # German only
            continue
        makt.append(("100", matnr, "E", f"Material {m}", f"MATERIAL {m}"))
        makt.append(("100", matnr, "D", f"Material {m} (DE)", f"MATERIAL {m} (DE)"))
    data["MAKT"] = (makt_cols, makt)

    matdoc_cols = ["MANDT", "MBLNR", "MJAHR", "ZEILE", "RECORD_TYPE", "VGART", "BLART", "BLDAT", "BUDAT", "CPUDT", "USNAM",
                   "XBLNR", "BKTXT", "BWART", "MATNR", "WERKS", "LGORT", "CHARG", "LIFNR", "KUNNR", "SHKZG", "WAERS",
                   "DMBTR", "MENGE", "MEINS", "EBELN", "EBELP", "KOSTL", "AUFNR"]
    matdoc = []
    for d in range(1, 81):
        mblnr = f"{4900000000 + d:010d}"
        budat = f"2026{rnd.randint(1, 9):02d}{rnd.randint(1, 28):02d}"
        for z in range(1, rnd.randint(2, 5)):
            bwart = rnd.choice(["101", "201", "261", "311", "601"])
            shkzg = "S" if bwart in ("101",) else "H"
            rec = "MDOC" if rnd.random() > 0.08 else "XXXX"
            matdoc.append(("100", mblnr, "2026", f"{z:04d}", rec, "WE", "WE", budat, budat, budat, "USER01", "", "",
                           bwart, f"{rnd.randint(1, 30):018d}", rnd.choice(["1000", "2000"]), "0001", "", "", "", shkzg,
                           "EUR", Decimal(rnd.randint(100, 99999)) / 100, Decimal(rnd.randint(1, 500)), "EA", "", "00000", "", ""))
    data["MATDOC"] = (matdoc_cols, matdoc)
    return data


def setup_demo(cursor, kb: KnowledgeBase, database: str = "TCODE_BREAKER", schema: str = "SAP_DEMO") -> dict[str, int]:
    """Create the demo schema with stub tables and load synthetic data. Returns row counts."""
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
    cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {database}.{schema}")
    counts: dict[str, int] = {}
    for table, (cols, rows) in _rows().items():
        ddl = ddl_for_table(kb, table, database, schema, replace=True)
        if ddl is None:
            raise RuntimeError(f"Table {table} missing from knowledge base")
        cursor.execute(ddl)
        placeholders = ", ".join(["%s"] * len(cols))
        cursor.executemany(
            f"INSERT INTO {database}.{schema}.{table} ({', '.join(cols)}) VALUES ({placeholders})",
            [tuple(str(v) if isinstance(v, Decimal) else v for v in r) for r in rows],
        )
        counts[table] = len(rows)
    return counts
