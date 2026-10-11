*&---------------------------------------------------------------------*
*& Report ZSF05_MONTHLY_REVENUE
*&---------------------------------------------------------------------*
*& Monthly revenue per airline: COLLECT aggregation, SELECT SINGLE
*& inside a loop (text lookup), substring of a DATS field.
*&---------------------------------------------------------------------*
REPORT zsf05_monthly_revenue.

TABLES: sbook.

SELECT-OPTIONS: s_carr FOR sbook-carrid,
                s_date FOR sbook-fldate.

TYPES: BEGIN OF ty_book,
         carrid    TYPE sbook-carrid,
         fldate    TYPE sbook-fldate,
         loccuram  TYPE sbook-loccuram,
         loccurkey TYPE sbook-loccurkey,
       END OF ty_book,
       BEGIN OF ty_sum,
         carrid    TYPE sbook-carrid,
         month     TYPE char6,
         loccurkey TYPE sbook-loccurkey,
         bookings  TYPE i,
         revenue   TYPE sbook-loccuram,
       END OF ty_sum,
       BEGIN OF ty_out,
         carrid    TYPE sbook-carrid,
         carrname  TYPE scarr-carrname,
         month     TYPE char6,
         loccurkey TYPE sbook-loccurkey,
         bookings  TYPE i,
         revenue   TYPE sbook-loccuram,
         avg_rev   TYPE sbook-loccuram,
       END OF ty_out.

DATA: gt_book TYPE STANDARD TABLE OF ty_book,
      gs_book TYPE ty_book,
      gt_sum  TYPE STANDARD TABLE OF ty_sum,
      gs_sum  TYPE ty_sum,
      gt_out  TYPE STANDARD TABLE OF ty_out,
      gs_out  TYPE ty_out,
      lv_name TYPE scarr-carrname,
      go_alv  TYPE REF TO cl_salv_table.

START-OF-SELECTION.

  SELECT carrid fldate loccuram loccurkey
    FROM sbook
    INTO TABLE gt_book
    WHERE carrid    IN s_carr
      AND fldate    IN s_date
      AND cancelled <> 'X'.

  LOOP AT gt_book INTO gs_book.
    CLEAR gs_sum.
    gs_sum-carrid    = gs_book-carrid.
    gs_sum-month     = gs_book-fldate(6).
    gs_sum-loccurkey = gs_book-loccurkey.
    gs_sum-bookings  = 1.
    gs_sum-revenue   = gs_book-loccuram.
    COLLECT gs_sum INTO gt_sum.
  ENDLOOP.

  LOOP AT gt_sum INTO gs_sum.
    CLEAR: gs_out, lv_name.
    MOVE-CORRESPONDING gs_sum TO gs_out.

    SELECT SINGLE carrname
      FROM scarr
      INTO lv_name
      WHERE carrid = gs_sum-carrid.
    gs_out-carrname = lv_name.

    IF gs_sum-bookings > 0.
      gs_out-avg_rev = gs_sum-revenue / gs_sum-bookings.
    ENDIF.
    APPEND gs_out TO gt_out.
  ENDLOOP.

  SORT gt_out BY carrid month.

  cl_salv_table=>factory(
    IMPORTING r_salv_table = go_alv
    CHANGING  t_table      = gt_out ).
  go_alv->display( ).
