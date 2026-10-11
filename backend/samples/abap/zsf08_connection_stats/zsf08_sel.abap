*&---------------------------------------------------------------------*
*& Include ZSF08_SEL
*&---------------------------------------------------------------------*
SELECTION-SCREEN BEGIN OF BLOCK b1 WITH FRAME TITLE TEXT-001.
SELECT-OPTIONS: s_carr FOR sflight-carrid,
                s_date FOR sflight-fldate.
SELECTION-SCREEN END OF BLOCK b1.
SELECTION-SCREEN BEGIN OF BLOCK b2 WITH FRAME TITLE TEXT-002.
PARAMETERS: p_mail TYPE ad_smtpadr,
            p_test AS CHECKBOX DEFAULT space.
SELECTION-SCREEN END OF BLOCK b2.
