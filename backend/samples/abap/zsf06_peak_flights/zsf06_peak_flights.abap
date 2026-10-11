*&---------------------------------------------------------------------*
*& Report ZSF06_PEAK_FLIGHTS
*&---------------------------------------------------------------------*
*& Peak flight per connection: nested FORMs, SORT DESCENDING +
*& DELETE ADJACENT DUPLICATES (top-1 per group), LOOP ... ASSIGNING
*& with IF/ELSEIF bands, DELETE WHERE filter on an internal table.
*&---------------------------------------------------------------------*
REPORT zsf06_peak_flights.

TABLES: sflight.

SELECT-OPTIONS: s_carr FOR sflight-carrid.
PARAMETERS:     p_minocc TYPE sflight-seatsocc DEFAULT 1.

TYPES: BEGIN OF ty_flight,
         carrid    TYPE sflight-carrid,
         connid    TYPE sflight-connid,
         fldate    TYPE sflight-fldate,
         planetype TYPE sflight-planetype,
         seatsmax  TYPE sflight-seatsmax,
         seatsocc  TYPE sflight-seatsocc,
         band      TYPE char10,
       END OF ty_flight.

DATA: gt_flight TYPE STANDARD TABLE OF ty_flight,
      go_alv    TYPE REF TO cl_salv_table.

FIELD-SYMBOLS: <ls_flight> TYPE ty_flight.

START-OF-SELECTION.
  PERFORM get_data.
  PERFORM keep_peak_per_connection.
  PERFORM classify.
  PERFORM display.

*&---------------------------------------------------------------------*
FORM get_data.
  PERFORM read_flights.
  PERFORM apply_min_occupancy.
ENDFORM.

FORM read_flights.
  SELECT carrid connid fldate planetype seatsmax seatsocc
    FROM sflight
    INTO CORRESPONDING FIELDS OF TABLE gt_flight
    WHERE carrid IN s_carr.
ENDFORM.

FORM apply_min_occupancy.
  DELETE gt_flight WHERE seatsocc < p_minocc.
ENDFORM.

*&---------------------------------------------------------------------*
FORM keep_peak_per_connection.
  SORT gt_flight BY carrid connid seatsocc DESCENDING fldate.
  DELETE ADJACENT DUPLICATES FROM gt_flight COMPARING carrid connid.
ENDFORM.

*&---------------------------------------------------------------------*
FORM classify.
  LOOP AT gt_flight ASSIGNING <ls_flight>.
    IF <ls_flight>-seatsocc >= <ls_flight>-seatsmax.
      <ls_flight>-band = 'FULL'.
    ELSEIF <ls_flight>-seatsocc * 2 >= <ls_flight>-seatsmax.
      <ls_flight>-band = 'HIGH'.
    ELSE.
      <ls_flight>-band = 'LOW'.
    ENDIF.
  ENDLOOP.
ENDFORM.

*&---------------------------------------------------------------------*
FORM display.
  SORT gt_flight BY carrid connid.
  cl_salv_table=>factory(
    IMPORTING r_salv_table = go_alv
    CHANGING  t_table      = gt_flight ).
  go_alv->display( ).
ENDFORM.

*&---------------------------------------------------------------------*
*& Unused helper kept from an older version (dead code).
FORM log_runtime.
  DATA lv_ts TYPE timestampl.
  GET TIME STAMP FIELD lv_ts.
  WRITE: / 'Runtime', lv_ts.
ENDFORM.
