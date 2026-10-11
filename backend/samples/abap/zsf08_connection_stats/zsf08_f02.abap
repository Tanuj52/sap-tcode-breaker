*&---------------------------------------------------------------------*
*& Include ZSF08_F02 - utilities (live but irrelevant to the output)
*&---------------------------------------------------------------------*
FORM init_defaults.
  gv_mail = sy-uname.
ENDFORM.

FORM check_authority.
  AUTHORITY-CHECK OBJECT 'S_CARRID'
    ID 'CARRID' DUMMY
    ID 'ACTVT'  FIELD '03'.
  IF sy-subrc <> 0.
    MESSAGE e001 WITH 'No authorization for airline data'.
  ENDIF.
ENDFORM.

FORM progress USING iv_text TYPE csequence.
  CALL FUNCTION 'SAPGUI_PROGRESS_INDICATOR'
    EXPORTING
      percentage = 50
      text       = iv_text.
ENDFORM.

FORM log_message USING iv_text TYPE csequence.
  DATA ls_log TYPE ty_log.
  GET TIME STAMP FIELD ls_log-ts.
  ls_log-text = iv_text.
  APPEND ls_log TO gt_log.
ENDFORM.

FORM send_mail USING iv_to TYPE ad_smtpadr.
  DATA: lo_send TYPE REF TO cl_bcs,
        lt_text TYPE soli_tab,
        ls_text TYPE soli.
  ls_text-line = 'Connection statistics report finished.'.
  APPEND ls_text TO lt_text.
  TRY.
      lo_send = cl_bcs=>create_persistent( ).
    CATCH cx_bcs.
      PERFORM log_message USING 'Mail failed'.
  ENDTRY.
ENDFORM.
