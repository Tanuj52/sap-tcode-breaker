*&---------------------------------------------------------------------*
*& Report ZS4_GOODS_MOVEMENTS
*&---------------------------------------------------------------------*
*& Classic goods-movement report written against MKPF/MSEG.
*& On S/4HANA these are compatibility views over MATDOC; a Snowflake
*& replica of S/4 typically only contains the physical MATDOC table.
*&---------------------------------------------------------------------*
REPORT zs4_goods_movements.

TABLES: mkpf, mseg.

SELECT-OPTIONS: s_werks FOR mseg-werks,
                s_matnr FOR mseg-matnr,
                s_budat FOR mkpf-budat,
                s_bwart FOR mseg-bwart.

TYPES: BEGIN OF ty_out,
         mblnr      TYPE mkpf-mblnr,
         mjahr      TYPE mkpf-mjahr,
         zeile      TYPE mseg-zeile,
         budat      TYPE mkpf-budat,
         matnr      TYPE mseg-matnr,
         maktx      TYPE makt-maktx,
         werks      TYPE mseg-werks,
         lgort      TYPE mseg-lgort,
         bwart      TYPE mseg-bwart,
         shkzg      TYPE mseg-shkzg,
         menge      TYPE mseg-menge,
         meins      TYPE mseg-meins,
         signed_qty TYPE mseg-menge,
       END OF ty_out,
       BEGIN OF ty_makt,
         matnr TYPE makt-matnr,
         maktx TYPE makt-maktx,
       END OF ty_makt.

DATA: gt_out  TYPE STANDARD TABLE OF ty_out,
      gt_makt TYPE SORTED TABLE OF ty_makt WITH UNIQUE KEY matnr,
      go_alv  TYPE REF TO cl_salv_table.

FIELD-SYMBOLS: <ls_out>  TYPE ty_out,
               <ls_makt> TYPE ty_makt.

START-OF-SELECTION.

  SELECT k~mblnr k~mjahr m~zeile k~budat m~matnr m~werks
         m~lgort m~bwart m~shkzg m~menge m~meins
    INTO CORRESPONDING FIELDS OF TABLE gt_out
    FROM mkpf AS k
    INNER JOIN mseg AS m
      ON  m~mblnr = k~mblnr
      AND m~mjahr = k~mjahr
    WHERE m~werks IN s_werks
      AND m~matnr IN s_matnr
      AND k~budat IN s_budat
      AND m~bwart IN s_bwart.

  IF gt_out IS NOT INITIAL.
    SELECT matnr maktx
      FROM makt
      INTO TABLE gt_makt
      FOR ALL ENTRIES IN gt_out
      WHERE matnr = gt_out-matnr
        AND spras = sy-langu.
  ENDIF.

  LOOP AT gt_out ASSIGNING <ls_out>.
    READ TABLE gt_makt ASSIGNING <ls_makt>
         WITH TABLE KEY matnr = <ls_out>-matnr.
    IF sy-subrc = 0.
      <ls_out>-maktx = <ls_makt>-maktx.
    ENDIF.

    IF <ls_out>-shkzg = 'H'.
      <ls_out>-signed_qty = <ls_out>-menge * -1.
    ELSE.
      <ls_out>-signed_qty = <ls_out>-menge.
    ENDIF.
  ENDLOOP.

  SORT gt_out BY budat mblnr zeile.

  cl_salv_table=>factory(
    IMPORTING r_salv_table = go_alv
    CHANGING  t_table      = gt_out ).
  go_alv->display( ).
