*&---------------------------------------------------------------------*
*& Report ZSF09_CARRIER_TOTALS
*&---------------------------------------------------------------------*
*& Control-break processing (AT END OF + SUM): totals per airline.
*& Deliberately outside the deterministic compiler -> exercises the
*& LLM translator for a single, well-scoped step.
*&---------------------------------------------------------------------*
REPORT zsf09_carrier_totals.

TABLES: sflight.

SELECT-OPTIONS: s_carr FOR sflight-carrid.

TYPES: BEGIN OF ty_flight,
         carrid   TYPE sflight-carrid,
         seatsmax TYPE sflight-seatsmax,
         seatsocc TYPE sflight-seatsocc,
       END OF ty_flight,
       BEGIN OF ty_out,
         carrid   TYPE sflight-carrid,
         seatsmax TYPE sflight-seatsmax,
         seatsocc TYPE sflight-seatsocc,
       END OF ty_out.

DATA: gt_flight TYPE STANDARD TABLE OF ty_flight,
      gs_flight TYPE ty_flight,
      gt_out    TYPE STANDARD TABLE OF ty_out,
      gs_out    TYPE ty_out,
      go_alv    TYPE REF TO cl_salv_table.

START-OF-SELECTION.

  SELECT carrid seatsmax seatsocc
    FROM sflight
    INTO TABLE gt_flight
    WHERE carrid IN s_carr.

  SORT gt_flight BY carrid.

  LOOP AT gt_flight INTO gs_flight.
    AT END OF carrid.
      SUM.
      gs_out-carrid   = gs_flight-carrid.
      gs_out-seatsmax = gs_flight-seatsmax.
      gs_out-seatsocc = gs_flight-seatsocc.
      APPEND gs_out TO gt_out.
    ENDAT.
  ENDLOOP.

  cl_salv_table=>factory(
    IMPORTING r_salv_table = go_alv
    CHANGING  t_table      = gt_out ).
  go_alv->display( ).
