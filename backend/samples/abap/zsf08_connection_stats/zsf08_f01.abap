*&---------------------------------------------------------------------*
*& Include ZSF08_F01 - business logic
*&---------------------------------------------------------------------*
FORM get_flights.
  SELECT carrid connid fldate seatsmax seatsocc
    FROM sflight
    INTO TABLE gt_flight
    WHERE carrid IN s_carr
      AND fldate IN s_date.
  gv_count = lines( gt_flight ).
  PERFORM progress USING 'Flights read'.
ENDFORM.

FORM get_connections.
  CHECK gt_flight IS NOT INITIAL.
  SELECT carrid connid cityfrom cityto
    FROM spfli
    INTO TABLE gt_conn
    FOR ALL ENTRIES IN gt_flight
    WHERE carrid = gt_flight-carrid
      AND connid = gt_flight-connid.
ENDFORM.

FORM aggregate.
  DATA ls_stat TYPE ty_stat.
  FIELD-SYMBOLS <ls_flight> TYPE ty_flight.
  LOOP AT gt_flight ASSIGNING <ls_flight>.
    CLEAR ls_stat.
    ls_stat-carrid   = <ls_flight>-carrid.
    ls_stat-connid   = <ls_flight>-connid.
    ls_stat-flights  = 1.
    ls_stat-seatsmax = <ls_flight>-seatsmax.
    ls_stat-seatsocc = <ls_flight>-seatsocc.
    COLLECT ls_stat INTO gt_stat.
    PERFORM progress USING 'Aggregating'.
  ENDLOOP.
ENDFORM.

FORM enrich_names.
  DATA ls_out TYPE ty_out.
  FIELD-SYMBOLS: <ls_stat>  TYPE ty_stat,
                 <ls_conn>  TYPE ty_conn,
                 <ls_scarr> TYPE scarr.

  SELECT * FROM scarr INTO TABLE gt_scarr.

  LOOP AT gt_stat ASSIGNING <ls_stat>.
    CLEAR ls_out.
    MOVE-CORRESPONDING <ls_stat> TO ls_out.
    READ TABLE gt_conn ASSIGNING <ls_conn>
         WITH TABLE KEY carrid = <ls_stat>-carrid connid = <ls_stat>-connid.
    IF sy-subrc = 0.
      ls_out-cityfrom = <ls_conn>-cityfrom.
      ls_out-cityto   = <ls_conn>-cityto.
    ENDIF.
    READ TABLE gt_scarr ASSIGNING <ls_scarr>
         WITH TABLE KEY carrid = <ls_stat>-carrid.
    IF sy-subrc = 0.
      ls_out-carrname = <ls_scarr>-carrname.
    ENDIF.
    APPEND ls_out TO gt_out.
  ENDLOOP.
  SORT gt_out BY carrid connid.
ENDFORM.

FORM display.
  IF p_test = 'X'.
    PERFORM log_message USING 'Test mode - no display'.
    RETURN.
  ENDIF.
  cl_salv_table=>factory(
    IMPORTING r_salv_table = go_alv
    CHANGING  t_table      = gt_out ).
  go_alv->display( ).
  IF p_mail IS NOT INITIAL.
    PERFORM send_mail USING p_mail.
  ENDIF.
ENDFORM.
