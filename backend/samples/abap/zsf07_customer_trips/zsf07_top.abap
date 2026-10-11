*&---------------------------------------------------------------------*
*& Include ZSF07_TOP - global declarations
*&---------------------------------------------------------------------*
TABLES: sbook, scustom.

TYPES: BEGIN OF ty_book,
         carrid    TYPE sbook-carrid,
         connid    TYPE sbook-connid,
         fldate    TYPE sbook-fldate,
         bookid    TYPE sbook-bookid,
         customid  TYPE sbook-customid,
         class     TYPE sbook-class,
         loccuram  TYPE sbook-loccuram,
         loccurkey TYPE sbook-loccurkey,
       END OF ty_book,
       BEGIN OF ty_cust,
         id       TYPE scustom-id,
         name     TYPE scustom-name,
         discount TYPE scustom-discount,
       END OF ty_cust,
       BEGIN OF ty_out,
         customid     TYPE sbook-customid,
         cust_ext     TYPE char10,
         cust_name    TYPE scustom-name,
         carrid       TYPE sbook-carrid,
         connid       TYPE sbook-connid,
         fldate       TYPE sbook-fldate,
         weekday      TYPE p,
         class        TYPE sbook-class,
         loccuram     TYPE sbook-loccuram,
         discount_pct TYPE i,
         net_amount   TYPE sbook-loccuram,
         loccurkey    TYPE sbook-loccurkey,
       END OF ty_out.

DATA: gt_book TYPE STANDARD TABLE OF ty_book,
      gt_cust TYPE HASHED TABLE OF ty_cust WITH UNIQUE KEY id,
      gt_out  TYPE STANDARD TABLE OF ty_out,
      go_alv  TYPE REF TO cl_salv_table.
