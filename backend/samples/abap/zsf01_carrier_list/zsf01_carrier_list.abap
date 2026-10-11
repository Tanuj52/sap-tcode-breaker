*&---------------------------------------------------------------------*
*& Report ZSF01_CARRIER_LIST
*&---------------------------------------------------------------------*
*& Simple carrier master list with selection screen and SALV output.
*&---------------------------------------------------------------------*
REPORT zsf01_carrier_list.

TABLES: scarr.

SELECT-OPTIONS: s_carr FOR scarr-carrid.
PARAMETERS:     p_curr TYPE scarr-currcode DEFAULT 'EUR'.

TYPES: BEGIN OF ty_carrier,
         carrid   TYPE scarr-carrid,
         carrname TYPE scarr-carrname,
         currcode TYPE scarr-currcode,
         url      TYPE scarr-url,
       END OF ty_carrier.

DATA: gt_carrier TYPE STANDARD TABLE OF ty_carrier,
      go_alv     TYPE REF TO cl_salv_table.

START-OF-SELECTION.

  SELECT carrid carrname currcode url
    FROM scarr
    INTO TABLE gt_carrier
    WHERE carrid   IN s_carr
      AND currcode =  p_curr.

  IF sy-subrc <> 0.
    MESSAGE 'No carriers found' TYPE 'S' DISPLAY LIKE 'E'.
    RETURN.
  ENDIF.

  SORT gt_carrier BY carrid.

  cl_salv_table=>factory(
    IMPORTING r_salv_table = go_alv
    CHANGING  t_table      = gt_carrier ).
  go_alv->display( ).
