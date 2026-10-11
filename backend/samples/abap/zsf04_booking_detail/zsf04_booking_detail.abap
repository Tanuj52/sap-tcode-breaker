*&---------------------------------------------------------------------*
*& Report ZSF04_BOOKING_DETAIL
*&---------------------------------------------------------------------*
*& Booking list with customer enrichment (READ TABLE, left-join
*& semantics), CASE-derived text columns, cancelled bookings excluded.
*&---------------------------------------------------------------------*
REPORT zsf04_booking_detail.

TABLES: sbook.

SELECT-OPTIONS: s_carr FOR sbook-carrid,
                s_date FOR sbook-fldate.
PARAMETERS:     p_smok AS CHECKBOX DEFAULT space.

TYPES: BEGIN OF ty_book,
         carrid   TYPE sbook-carrid,
         connid   TYPE sbook-connid,
         fldate   TYPE sbook-fldate,
         bookid   TYPE sbook-bookid,
         customid TYPE sbook-customid,
         class    TYPE sbook-class,
         smoker   TYPE sbook-smoker,
         loccuram TYPE sbook-loccuram,
         loccurkey TYPE sbook-loccurkey,
       END OF ty_book,
       BEGIN OF ty_cust,
         id      TYPE scustom-id,
         name    TYPE scustom-name,
         city    TYPE scustom-city,
         country TYPE scustom-country,
       END OF ty_cust,
       BEGIN OF ty_out,
         carrid     TYPE sbook-carrid,
         connid     TYPE sbook-connid,
         fldate     TYPE sbook-fldate,
         bookid     TYPE sbook-bookid,
         customid   TYPE sbook-customid,
         cust_name  TYPE scustom-name,
         cust_city  TYPE scustom-city,
         class_text TYPE char10,
         smoker_txt TYPE char3,
         loccuram   TYPE sbook-loccuram,
         loccurkey  TYPE sbook-loccurkey,
       END OF ty_out.

DATA: gt_book TYPE STANDARD TABLE OF ty_book,
      gt_cust TYPE SORTED TABLE OF ty_cust WITH UNIQUE KEY id,
      gt_out  TYPE STANDARD TABLE OF ty_out.

FIELD-SYMBOLS: <ls_book> TYPE ty_book,
               <ls_cust> TYPE ty_cust.

DATA: gs_out TYPE ty_out,
      go_alv TYPE REF TO cl_salv_table.

START-OF-SELECTION.

  SELECT carrid connid fldate bookid customid class smoker loccuram loccurkey
    FROM sbook
    INTO TABLE gt_book
    WHERE carrid    IN s_carr
      AND fldate    IN s_date
      AND cancelled = space.

  IF p_smok = 'X'.
    DELETE gt_book WHERE smoker <> 'X'.
  ENDIF.

  IF gt_book IS NOT INITIAL.
    SELECT id name city country
      FROM scustom
      INTO TABLE gt_cust
      FOR ALL ENTRIES IN gt_book
      WHERE id = gt_book-customid.
  ENDIF.

  LOOP AT gt_book ASSIGNING <ls_book>.
    CLEAR gs_out.
    MOVE-CORRESPONDING <ls_book> TO gs_out.

    READ TABLE gt_cust ASSIGNING <ls_cust>
         WITH TABLE KEY id = <ls_book>-customid.
    IF sy-subrc = 0.
      gs_out-cust_name = <ls_cust>-name.
      gs_out-cust_city = <ls_cust>-city.
    ENDIF.

    CASE <ls_book>-class.
      WHEN 'F'.
        gs_out-class_text = 'First'.
      WHEN 'C'.
        gs_out-class_text = 'Business'.
      WHEN 'Y'.
        gs_out-class_text = 'Economy'.
      WHEN OTHERS.
        gs_out-class_text = 'Unknown'.
    ENDCASE.

    IF <ls_book>-smoker = 'X'.
      gs_out-smoker_txt = 'Yes'.
    ELSE.
      gs_out-smoker_txt = 'No'.
    ENDIF.

    APPEND gs_out TO gt_out.
  ENDLOOP.

  SORT gt_out BY carrid connid fldate bookid.

  cl_salv_table=>factory(
    IMPORTING r_salv_table = go_alv
    CHANGING  t_table      = gt_out ).
  go_alv->display( ).
