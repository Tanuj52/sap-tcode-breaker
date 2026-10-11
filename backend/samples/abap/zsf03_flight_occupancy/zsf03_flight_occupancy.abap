*&---------------------------------------------------------------------*
*& Report ZSF03_FLIGHT_OCCUPANCY
*&---------------------------------------------------------------------*
*& FOR ALL ENTRIES chain SPFLI -> SFLIGHT, LOOP + READ TABLE
*& enrichment, derived columns (free seats, occupancy %).
*&---------------------------------------------------------------------*
REPORT zsf03_flight_occupancy.

TABLES: sflight.

SELECT-OPTIONS: s_carr FOR sflight-carrid,
                s_date FOR sflight-fldate.

TYPES: BEGIN OF ty_spfli,
         carrid   TYPE spfli-carrid,
         connid   TYPE spfli-connid,
         cityfrom TYPE spfli-cityfrom,
         cityto   TYPE spfli-cityto,
       END OF ty_spfli,
       BEGIN OF ty_flight,
         carrid   TYPE sflight-carrid,
         connid   TYPE sflight-connid,
         fldate   TYPE sflight-fldate,
         price    TYPE sflight-price,
         currency TYPE sflight-currency,
         seatsmax TYPE sflight-seatsmax,
         seatsocc TYPE sflight-seatsocc,
       END OF ty_flight,
       BEGIN OF ty_out,
         carrid    TYPE sflight-carrid,
         connid    TYPE sflight-connid,
         cityfrom  TYPE spfli-cityfrom,
         cityto    TYPE spfli-cityto,
         fldate    TYPE sflight-fldate,
         price     TYPE sflight-price,
         currency  TYPE sflight-currency,
         seatsmax  TYPE sflight-seatsmax,
         seatsocc  TYPE sflight-seatsocc,
         seatsfree TYPE i,
         occ_pct   TYPE p LENGTH 5 DECIMALS 2,
       END OF ty_out.

DATA: gt_spfli  TYPE STANDARD TABLE OF ty_spfli,
      gs_spfli  TYPE ty_spfli,
      gt_flight TYPE STANDARD TABLE OF ty_flight,
      gs_flight TYPE ty_flight,
      gt_out    TYPE STANDARD TABLE OF ty_out,
      gs_out    TYPE ty_out,
      go_alv    TYPE REF TO cl_salv_table.

START-OF-SELECTION.

  SELECT carrid connid cityfrom cityto
    FROM spfli
    INTO TABLE gt_spfli
    WHERE carrid IN s_carr.

  IF gt_spfli IS NOT INITIAL.
    SELECT carrid connid fldate price currency seatsmax seatsocc
      FROM sflight
      INTO TABLE gt_flight
      FOR ALL ENTRIES IN gt_spfli
      WHERE carrid = gt_spfli-carrid
        AND connid = gt_spfli-connid
        AND fldate IN s_date.
  ENDIF.

  SORT gt_spfli BY carrid connid.

  LOOP AT gt_flight INTO gs_flight.
    CLEAR gs_out.
    READ TABLE gt_spfli INTO gs_spfli
         WITH KEY carrid = gs_flight-carrid
                  connid = gs_flight-connid
         BINARY SEARCH.
    IF sy-subrc = 0.
      gs_out-cityfrom = gs_spfli-cityfrom.
      gs_out-cityto   = gs_spfli-cityto.
    ENDIF.

    gs_out-carrid    = gs_flight-carrid.
    gs_out-connid    = gs_flight-connid.
    gs_out-fldate    = gs_flight-fldate.
    gs_out-price     = gs_flight-price.
    gs_out-currency  = gs_flight-currency.
    gs_out-seatsmax  = gs_flight-seatsmax.
    gs_out-seatsocc  = gs_flight-seatsocc.
    gs_out-seatsfree = gs_flight-seatsmax - gs_flight-seatsocc.

    IF gs_flight-seatsmax > 0.
      gs_out-occ_pct = gs_flight-seatsocc * 100 / gs_flight-seatsmax.
    ENDIF.

    APPEND gs_out TO gt_out.
  ENDLOOP.

  SORT gt_out BY carrid connid fldate.

  cl_salv_table=>factory(
    IMPORTING r_salv_table = go_alv
    CHANGING  t_table      = gt_out ).
  go_alv->display( ).
