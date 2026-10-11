*&---------------------------------------------------------------------*
*& Report ZSF08_CONNECTION_STATS
*&---------------------------------------------------------------------*
*& Connection statistics (large generated report used for slicing tests)
*&---------------------------------------------------------------------*
REPORT zsf08_connection_stats MESSAGE-ID zsf.

INCLUDE zsf08_top.
INCLUDE zsf08_sel.

INITIALIZATION.
  PERFORM init_defaults.

AT SELECTION-SCREEN.
  PERFORM check_authority.

START-OF-SELECTION.
  PERFORM log_message USING 'Start of selection'.
  PERFORM get_flights.
  PERFORM get_connections.
  PERFORM aggregate.
  PERFORM enrich_names.
  PERFORM log_message USING 'End of selection'.

END-OF-SELECTION.
  PERFORM display.

INCLUDE zsf08_f01.
INCLUDE zsf08_f02.
INCLUDE zsf08_f03.
