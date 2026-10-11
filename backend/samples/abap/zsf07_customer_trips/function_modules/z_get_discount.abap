FUNCTION z_get_discount.
*"----------------------------------------------------------------------
*"*"Local Interface:
*"  IMPORTING
*"     VALUE(IV_CLASS) TYPE  S_CLASS
*"     VALUE(IV_CUST_DISCOUNT) TYPE  S_DISCOUNT
*"  EXPORTING
*"     VALUE(EV_PCT) TYPE  I
*"----------------------------------------------------------------------
  IF iv_cust_discount > 0.
    ev_pct = iv_cust_discount.
  ELSEIF iv_class = 'F'.
    ev_pct = 10.
  ELSEIF iv_class = 'C'.
    ev_pct = 5.
  ELSE.
    ev_pct = 0.
  ENDIF.
ENDFUNCTION.
