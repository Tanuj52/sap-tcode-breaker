*&---------------------------------------------------------------------*
*& Report ZS4_SALES_STATUS
*&---------------------------------------------------------------------*
*& Modern ABAP (7.40+): new Open SQL syntax, inline declarations,
*& VALUE #( FOR ... ), COND, REDUCE. Reads VBUK, whose header status
*& fields were moved into VBAK in S/4HANA.
*&---------------------------------------------------------------------*
REPORT zs4_sales_status.

TABLES: vbak.

SELECT-OPTIONS: s_vkorg FOR vbak-vkorg,
                s_erdat FOR vbak-erdat.
PARAMETERS:     p_open AS CHECKBOX DEFAULT 'X'.

TYPES: BEGIN OF ty_out,
         vbeln      TYPE vbak-vbeln,
         erdat      TYPE vbak-erdat,
         kunnr      TYPE vbak-kunnr,
         name1      TYPE kna1-name1,
         netwr      TYPE vbak-netwr,
         waerk      TYPE vbak-waerk,
         gbstk      TYPE vbuk-gbstk,
         status_txt TYPE char20,
         item_count TYPE i,
       END OF ty_out,
       tt_out TYPE STANDARD TABLE OF ty_out WITH EMPTY KEY.

START-OF-SELECTION.

  SELECT FROM vbak AS h
    INNER JOIN vbuk AS s ON s~vbeln = h~vbeln
    LEFT OUTER JOIN kna1 AS c ON c~kunnr = h~kunnr
    FIELDS h~vbeln, h~erdat, h~kunnr, c~name1, h~netwr, h~waerk, s~gbstk
    WHERE h~vkorg IN @s_vkorg
      AND h~erdat IN @s_erdat
    INTO TABLE @DATA(lt_head).

  IF p_open = abap_true.
    DELETE lt_head WHERE gbstk = 'C'.
  ENDIF.

  IF lt_head IS NOT INITIAL.
    SELECT FROM vbap
      FIELDS vbeln, posnr
      FOR ALL ENTRIES IN @lt_head
      WHERE vbeln = @lt_head-vbeln
      INTO TABLE @DATA(lt_items).
  ENDIF.

  DATA(lt_out) = VALUE tt_out(
    FOR ls_head IN lt_head
    ( vbeln      = ls_head-vbeln
      erdat      = ls_head-erdat
      kunnr      = ls_head-kunnr
      name1      = ls_head-name1
      netwr      = ls_head-netwr
      waerk      = ls_head-waerk
      gbstk      = ls_head-gbstk
      status_txt = COND #( WHEN ls_head-gbstk = 'A' THEN 'Open'
                           WHEN ls_head-gbstk = 'B' THEN 'In Process'
                           WHEN ls_head-gbstk = 'C' THEN 'Completed'
                           ELSE 'Unknown' )
      item_count = REDUCE i( INIT n = 0
                             FOR ls_item IN lt_items
                             WHERE ( vbeln = ls_head-vbeln )
                             NEXT n = n + 1 ) ) ).

  SORT lt_out BY vbeln.

  cl_salv_table=>factory(
    IMPORTING r_salv_table = DATA(lo_alv)
    CHANGING  t_table      = lt_out ).
  lo_alv->display( ).
