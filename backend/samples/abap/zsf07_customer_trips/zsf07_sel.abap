*&---------------------------------------------------------------------*
*& Include ZSF07_SEL - selection screen
*&---------------------------------------------------------------------*
SELECTION-SCREEN BEGIN OF BLOCK b1 WITH FRAME TITLE TEXT-001.
SELECT-OPTIONS: s_cust FOR scustom-id,
                s_carr FOR sbook-carrid.
SELECTION-SCREEN END OF BLOCK b1.
