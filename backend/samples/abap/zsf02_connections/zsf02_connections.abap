*&---------------------------------------------------------------------*
*& Report ZSF02_CONNECTIONS
*&---------------------------------------------------------------------*
*& Carrier connections: SCARR x SPFLI join, classic ALV with a field
*& catalog that controls which columns are shown and in which order.
*&---------------------------------------------------------------------*
REPORT zsf02_connections.

TYPE-POOLS: slis.

TABLES: spfli.

SELECT-OPTIONS: s_carr FOR spfli-carrid,
                s_ctry FOR spfli-countryfr.

TYPES: BEGIN OF ty_conn,
         carrid    TYPE spfli-carrid,
         carrname  TYPE scarr-carrname,
         connid    TYPE spfli-connid,
         cityfrom  TYPE spfli-cityfrom,
         cityto    TYPE spfli-cityto,
         distance  TYPE spfli-distance,
         distid    TYPE spfli-distid,
         fltime    TYPE spfli-fltime,
         airpfrom  TYPE spfli-airpfrom,
       END OF ty_conn.

DATA: gt_conn TYPE STANDARD TABLE OF ty_conn,
      gt_fcat TYPE slis_t_fieldcat_alv,
      gs_fcat TYPE slis_fieldcat_alv.

START-OF-SELECTION.
  PERFORM get_data.
  PERFORM build_fieldcat.
  PERFORM display.

*&---------------------------------------------------------------------*
FORM get_data.
  SELECT p~carrid c~carrname p~connid p~cityfrom p~cityto
         p~distance p~distid p~fltime p~airpfrom
    INTO TABLE gt_conn
    FROM spfli AS p
    INNER JOIN scarr AS c ON c~carrid = p~carrid
    WHERE p~carrid    IN s_carr
      AND p~countryfr IN s_ctry
      AND p~distance  >  0.

  SORT gt_conn BY carrid connid.
ENDFORM.

*&---------------------------------------------------------------------*
FORM build_fieldcat.
  CLEAR gs_fcat.
  gs_fcat-fieldname = 'CARRID'.
  gs_fcat-seltext_m = 'Airline'.
  APPEND gs_fcat TO gt_fcat.

  CLEAR gs_fcat.
  gs_fcat-fieldname = 'CARRNAME'.
  gs_fcat-seltext_m = 'Airline Name'.
  APPEND gs_fcat TO gt_fcat.

  CLEAR gs_fcat.
  gs_fcat-fieldname = 'CONNID'.
  gs_fcat-seltext_m = 'Connection'.
  APPEND gs_fcat TO gt_fcat.

  CLEAR gs_fcat.
  gs_fcat-fieldname = 'CITYFROM'.
  gs_fcat-seltext_m = 'From'.
  APPEND gs_fcat TO gt_fcat.

  CLEAR gs_fcat.
  gs_fcat-fieldname = 'CITYTO'.
  gs_fcat-seltext_m = 'To'.
  APPEND gs_fcat TO gt_fcat.

  CLEAR gs_fcat.
  gs_fcat-fieldname = 'DISTANCE'.
  gs_fcat-seltext_m = 'Distance'.
  APPEND gs_fcat TO gt_fcat.

  CLEAR gs_fcat.
  gs_fcat-fieldname = 'DISTID'.
  gs_fcat-seltext_m = 'Unit'.
  APPEND gs_fcat TO gt_fcat.

  CLEAR gs_fcat.
  gs_fcat-fieldname = 'AIRPFROM'.
  gs_fcat-seltext_m = 'Departure Airport'.
  gs_fcat-no_out    = 'X'.
  APPEND gs_fcat TO gt_fcat.
ENDFORM.

*&---------------------------------------------------------------------*
FORM display.
  CALL FUNCTION 'REUSE_ALV_GRID_DISPLAY'
    EXPORTING
      i_callback_program = sy-repid
      it_fieldcat        = gt_fcat
    TABLES
      t_outtab           = gt_conn
    EXCEPTIONS
      program_error      = 1
      OTHERS             = 2.
  IF sy-subrc <> 0.
    MESSAGE 'ALV display failed' TYPE 'E'.
  ENDIF.
ENDFORM.
