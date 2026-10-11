*&---------------------------------------------------------------------*
*& Report ZSF07_CUSTOMER_TRIPS
*&---------------------------------------------------------------------*
*& Customer trips with discount: includes, standard FMs
*& (CONVERSION_EXIT_ALPHA_OUTPUT, DATE_COMPUTE_DAY) and a custom FM
*& (Z_GET_DISCOUNT) whose source is supplied separately.
*&---------------------------------------------------------------------*
REPORT zsf07_customer_trips.

INCLUDE zsf07_top.
INCLUDE zsf07_sel.

START-OF-SELECTION.
  PERFORM get_bookings.
  PERFORM get_customers.
  PERFORM build_output.
  PERFORM display.

INCLUDE zsf07_f01.
