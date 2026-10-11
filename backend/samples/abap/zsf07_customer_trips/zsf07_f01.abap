*&---------------------------------------------------------------------*
*& Include ZSF07_F01 - subroutines
*&---------------------------------------------------------------------*

FORM get_bookings.
  SELECT carrid connid fldate bookid customid class loccuram loccurkey
    FROM sbook
    INTO TABLE gt_book
    WHERE customid  IN s_cust
      AND carrid    IN s_carr
      AND cancelled =  space.
ENDFORM.

FORM get_customers.
  CHECK gt_book IS NOT INITIAL.
  SELECT id name discount
    FROM scustom
    INTO TABLE gt_cust
    FOR ALL ENTRIES IN gt_book
    WHERE id = gt_book-customid.
ENDFORM.

FORM build_output.
  DATA: ls_out TYPE ty_out,
        lv_day TYPE p.
  FIELD-SYMBOLS: <ls_book> TYPE ty_book,
                 <ls_cust> TYPE ty_cust.

  LOOP AT gt_book ASSIGNING <ls_book>.
    CLEAR ls_out.
    ls_out-customid  = <ls_book>-customid.
    ls_out-carrid    = <ls_book>-carrid.
    ls_out-connid    = <ls_book>-connid.
    ls_out-fldate    = <ls_book>-fldate.
    ls_out-class     = <ls_book>-class.
    ls_out-loccuram  = <ls_book>-loccuram.
    ls_out-loccurkey = <ls_book>-loccurkey.

    CALL FUNCTION 'CONVERSION_EXIT_ALPHA_OUTPUT'
      EXPORTING
        input  = <ls_book>-customid
      IMPORTING
        output = ls_out-cust_ext.

    CALL FUNCTION 'DATE_COMPUTE_DAY'
      EXPORTING
        date = <ls_book>-fldate
      IMPORTING
        day  = lv_day.
    ls_out-weekday = lv_day.

    READ TABLE gt_cust ASSIGNING <ls_cust>
         WITH TABLE KEY id = <ls_book>-customid.
    IF sy-subrc = 0.
      ls_out-cust_name = <ls_cust>-name.
      CALL FUNCTION 'Z_GET_DISCOUNT'
        EXPORTING
          iv_class         = <ls_book>-class
          iv_cust_discount = <ls_cust>-discount
        IMPORTING
          ev_pct           = ls_out-discount_pct.
    ENDIF.

    ls_out-net_amount = ls_out-loccuram * ( 100 - ls_out-discount_pct ) / 100.
    APPEND ls_out TO gt_out.
  ENDLOOP.

  SORT gt_out BY customid fldate carrid connid.
ENDFORM.

FORM display.
  cl_salv_table=>factory(
    IMPORTING r_salv_table = go_alv
    CHANGING  t_table      = gt_out ).
  go_alv->display( ).
ENDFORM.
