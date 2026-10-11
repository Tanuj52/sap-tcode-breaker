*&---------------------------------------------------------------------*
*& Include ZSF08_F03 - obsolete subroutines (dead code)
*&---------------------------------------------------------------------*

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0001 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0001 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0001 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0001 TYPE sflight,
        lv_sum_0001 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0001
    WHERE carrid = iv_carrid
      AND seatsocc > 7.
  LOOP AT lt_tmp_0001 INTO ls_tmp_0001.
    lv_sum_0001 = lv_sum_0001 + ls_tmp_0001-seatsocc.
    IF lv_sum_0001 > 1001.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0001', lv_sum_0001.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0002 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0002 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0002 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0002 TYPE sflight,
        lv_sum_0002 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0002
    WHERE carrid = iv_carrid
      AND seatsocc > 14.
  LOOP AT lt_tmp_0002 INTO ls_tmp_0002.
    lv_sum_0002 = lv_sum_0002 + ls_tmp_0002-seatsocc.
    IF lv_sum_0002 > 1002.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0002', lv_sum_0002.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0003 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0003 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0003 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0003 TYPE sflight,
        lv_sum_0003 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0003
    WHERE carrid = iv_carrid
      AND seatsocc > 21.
  LOOP AT lt_tmp_0003 INTO ls_tmp_0003.
    lv_sum_0003 = lv_sum_0003 + ls_tmp_0003-seatsocc.
    IF lv_sum_0003 > 1003.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0003', lv_sum_0003.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0004 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0004 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0004 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0004 TYPE sflight,
        lv_sum_0004 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0004
    WHERE carrid = iv_carrid
      AND seatsocc > 28.
  LOOP AT lt_tmp_0004 INTO ls_tmp_0004.
    lv_sum_0004 = lv_sum_0004 + ls_tmp_0004-seatsocc.
    IF lv_sum_0004 > 1004.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0004', lv_sum_0004.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0005 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0005 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0005 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0005 TYPE sflight,
        lv_sum_0005 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0005
    WHERE carrid = iv_carrid
      AND seatsocc > 35.
  LOOP AT lt_tmp_0005 INTO ls_tmp_0005.
    lv_sum_0005 = lv_sum_0005 + ls_tmp_0005-seatsocc.
    IF lv_sum_0005 > 1005.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0005', lv_sum_0005.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0006 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0006 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0006 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0006 TYPE sflight,
        lv_sum_0006 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0006
    WHERE carrid = iv_carrid
      AND seatsocc > 42.
  LOOP AT lt_tmp_0006 INTO ls_tmp_0006.
    lv_sum_0006 = lv_sum_0006 + ls_tmp_0006-seatsocc.
    IF lv_sum_0006 > 1006.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0006', lv_sum_0006.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0007 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0007 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0007 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0007 TYPE sflight,
        lv_sum_0007 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0007
    WHERE carrid = iv_carrid
      AND seatsocc > 49.
  LOOP AT lt_tmp_0007 INTO ls_tmp_0007.
    lv_sum_0007 = lv_sum_0007 + ls_tmp_0007-seatsocc.
    IF lv_sum_0007 > 1007.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0007', lv_sum_0007.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0008 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0008 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0008 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0008 TYPE sflight,
        lv_sum_0008 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0008
    WHERE carrid = iv_carrid
      AND seatsocc > 56.
  LOOP AT lt_tmp_0008 INTO ls_tmp_0008.
    lv_sum_0008 = lv_sum_0008 + ls_tmp_0008-seatsocc.
    IF lv_sum_0008 > 1008.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0008', lv_sum_0008.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0009 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0009 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0009 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0009 TYPE sflight,
        lv_sum_0009 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0009
    WHERE carrid = iv_carrid
      AND seatsocc > 63.
  LOOP AT lt_tmp_0009 INTO ls_tmp_0009.
    lv_sum_0009 = lv_sum_0009 + ls_tmp_0009-seatsocc.
    IF lv_sum_0009 > 1009.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0009', lv_sum_0009.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0010 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0010 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0010 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0010 TYPE sflight,
        lv_sum_0010 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0010
    WHERE carrid = iv_carrid
      AND seatsocc > 70.
  LOOP AT lt_tmp_0010 INTO ls_tmp_0010.
    lv_sum_0010 = lv_sum_0010 + ls_tmp_0010-seatsocc.
    IF lv_sum_0010 > 1010.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0010', lv_sum_0010.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0011 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0011 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0011 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0011 TYPE sflight,
        lv_sum_0011 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0011
    WHERE carrid = iv_carrid
      AND seatsocc > 77.
  LOOP AT lt_tmp_0011 INTO ls_tmp_0011.
    lv_sum_0011 = lv_sum_0011 + ls_tmp_0011-seatsocc.
    IF lv_sum_0011 > 1011.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0011', lv_sum_0011.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0012 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0012 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0012 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0012 TYPE sflight,
        lv_sum_0012 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0012
    WHERE carrid = iv_carrid
      AND seatsocc > 84.
  LOOP AT lt_tmp_0012 INTO ls_tmp_0012.
    lv_sum_0012 = lv_sum_0012 + ls_tmp_0012-seatsocc.
    IF lv_sum_0012 > 1012.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0012', lv_sum_0012.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0013 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0013 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0013 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0013 TYPE sflight,
        lv_sum_0013 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0013
    WHERE carrid = iv_carrid
      AND seatsocc > 91.
  LOOP AT lt_tmp_0013 INTO ls_tmp_0013.
    lv_sum_0013 = lv_sum_0013 + ls_tmp_0013-seatsocc.
    IF lv_sum_0013 > 1013.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0013', lv_sum_0013.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0014 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0014 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0014 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0014 TYPE sflight,
        lv_sum_0014 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0014
    WHERE carrid = iv_carrid
      AND seatsocc > 98.
  LOOP AT lt_tmp_0014 INTO ls_tmp_0014.
    lv_sum_0014 = lv_sum_0014 + ls_tmp_0014-seatsocc.
    IF lv_sum_0014 > 1014.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0014', lv_sum_0014.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0015 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0015 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0015 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0015 TYPE sflight,
        lv_sum_0015 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0015
    WHERE carrid = iv_carrid
      AND seatsocc > 105.
  LOOP AT lt_tmp_0015 INTO ls_tmp_0015.
    lv_sum_0015 = lv_sum_0015 + ls_tmp_0015-seatsocc.
    IF lv_sum_0015 > 1015.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0015', lv_sum_0015.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0016 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0016 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0016 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0016 TYPE sflight,
        lv_sum_0016 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0016
    WHERE carrid = iv_carrid
      AND seatsocc > 112.
  LOOP AT lt_tmp_0016 INTO ls_tmp_0016.
    lv_sum_0016 = lv_sum_0016 + ls_tmp_0016-seatsocc.
    IF lv_sum_0016 > 1016.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0016', lv_sum_0016.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0017 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0017 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0017 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0017 TYPE sflight,
        lv_sum_0017 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0017
    WHERE carrid = iv_carrid
      AND seatsocc > 119.
  LOOP AT lt_tmp_0017 INTO ls_tmp_0017.
    lv_sum_0017 = lv_sum_0017 + ls_tmp_0017-seatsocc.
    IF lv_sum_0017 > 1017.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0017', lv_sum_0017.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0018 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0018 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0018 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0018 TYPE sflight,
        lv_sum_0018 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0018
    WHERE carrid = iv_carrid
      AND seatsocc > 126.
  LOOP AT lt_tmp_0018 INTO ls_tmp_0018.
    lv_sum_0018 = lv_sum_0018 + ls_tmp_0018-seatsocc.
    IF lv_sum_0018 > 1018.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0018', lv_sum_0018.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0019 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0019 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0019 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0019 TYPE sflight,
        lv_sum_0019 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0019
    WHERE carrid = iv_carrid
      AND seatsocc > 133.
  LOOP AT lt_tmp_0019 INTO ls_tmp_0019.
    lv_sum_0019 = lv_sum_0019 + ls_tmp_0019-seatsocc.
    IF lv_sum_0019 > 1019.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0019', lv_sum_0019.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0020 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0020 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0020 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0020 TYPE sflight,
        lv_sum_0020 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0020
    WHERE carrid = iv_carrid
      AND seatsocc > 140.
  LOOP AT lt_tmp_0020 INTO ls_tmp_0020.
    lv_sum_0020 = lv_sum_0020 + ls_tmp_0020-seatsocc.
    IF lv_sum_0020 > 1020.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0020', lv_sum_0020.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0021 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0021 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0021 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0021 TYPE sflight,
        lv_sum_0021 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0021
    WHERE carrid = iv_carrid
      AND seatsocc > 147.
  LOOP AT lt_tmp_0021 INTO ls_tmp_0021.
    lv_sum_0021 = lv_sum_0021 + ls_tmp_0021-seatsocc.
    IF lv_sum_0021 > 1021.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0021', lv_sum_0021.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0022 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0022 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0022 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0022 TYPE sflight,
        lv_sum_0022 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0022
    WHERE carrid = iv_carrid
      AND seatsocc > 154.
  LOOP AT lt_tmp_0022 INTO ls_tmp_0022.
    lv_sum_0022 = lv_sum_0022 + ls_tmp_0022-seatsocc.
    IF lv_sum_0022 > 1022.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0022', lv_sum_0022.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0023 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0023 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0023 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0023 TYPE sflight,
        lv_sum_0023 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0023
    WHERE carrid = iv_carrid
      AND seatsocc > 161.
  LOOP AT lt_tmp_0023 INTO ls_tmp_0023.
    lv_sum_0023 = lv_sum_0023 + ls_tmp_0023-seatsocc.
    IF lv_sum_0023 > 1023.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0023', lv_sum_0023.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0024 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0024 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0024 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0024 TYPE sflight,
        lv_sum_0024 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0024
    WHERE carrid = iv_carrid
      AND seatsocc > 168.
  LOOP AT lt_tmp_0024 INTO ls_tmp_0024.
    lv_sum_0024 = lv_sum_0024 + ls_tmp_0024-seatsocc.
    IF lv_sum_0024 > 1024.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0024', lv_sum_0024.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0025 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0025 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0025 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0025 TYPE sflight,
        lv_sum_0025 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0025
    WHERE carrid = iv_carrid
      AND seatsocc > 175.
  LOOP AT lt_tmp_0025 INTO ls_tmp_0025.
    lv_sum_0025 = lv_sum_0025 + ls_tmp_0025-seatsocc.
    IF lv_sum_0025 > 1025.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0025', lv_sum_0025.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0026 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0026 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0026 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0026 TYPE sflight,
        lv_sum_0026 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0026
    WHERE carrid = iv_carrid
      AND seatsocc > 182.
  LOOP AT lt_tmp_0026 INTO ls_tmp_0026.
    lv_sum_0026 = lv_sum_0026 + ls_tmp_0026-seatsocc.
    IF lv_sum_0026 > 1026.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0026', lv_sum_0026.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0027 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0027 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0027 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0027 TYPE sflight,
        lv_sum_0027 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0027
    WHERE carrid = iv_carrid
      AND seatsocc > 189.
  LOOP AT lt_tmp_0027 INTO ls_tmp_0027.
    lv_sum_0027 = lv_sum_0027 + ls_tmp_0027-seatsocc.
    IF lv_sum_0027 > 1027.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0027', lv_sum_0027.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0028 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0028 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0028 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0028 TYPE sflight,
        lv_sum_0028 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0028
    WHERE carrid = iv_carrid
      AND seatsocc > 196.
  LOOP AT lt_tmp_0028 INTO ls_tmp_0028.
    lv_sum_0028 = lv_sum_0028 + ls_tmp_0028-seatsocc.
    IF lv_sum_0028 > 1028.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0028', lv_sum_0028.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0029 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0029 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0029 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0029 TYPE sflight,
        lv_sum_0029 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0029
    WHERE carrid = iv_carrid
      AND seatsocc > 203.
  LOOP AT lt_tmp_0029 INTO ls_tmp_0029.
    lv_sum_0029 = lv_sum_0029 + ls_tmp_0029-seatsocc.
    IF lv_sum_0029 > 1029.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0029', lv_sum_0029.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0030 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0030 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0030 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0030 TYPE sflight,
        lv_sum_0030 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0030
    WHERE carrid = iv_carrid
      AND seatsocc > 210.
  LOOP AT lt_tmp_0030 INTO ls_tmp_0030.
    lv_sum_0030 = lv_sum_0030 + ls_tmp_0030-seatsocc.
    IF lv_sum_0030 > 1030.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0030', lv_sum_0030.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0031 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0031 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0031 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0031 TYPE sflight,
        lv_sum_0031 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0031
    WHERE carrid = iv_carrid
      AND seatsocc > 217.
  LOOP AT lt_tmp_0031 INTO ls_tmp_0031.
    lv_sum_0031 = lv_sum_0031 + ls_tmp_0031-seatsocc.
    IF lv_sum_0031 > 1031.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0031', lv_sum_0031.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0032 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0032 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0032 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0032 TYPE sflight,
        lv_sum_0032 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0032
    WHERE carrid = iv_carrid
      AND seatsocc > 224.
  LOOP AT lt_tmp_0032 INTO ls_tmp_0032.
    lv_sum_0032 = lv_sum_0032 + ls_tmp_0032-seatsocc.
    IF lv_sum_0032 > 1032.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0032', lv_sum_0032.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0033 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0033 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0033 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0033 TYPE sflight,
        lv_sum_0033 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0033
    WHERE carrid = iv_carrid
      AND seatsocc > 231.
  LOOP AT lt_tmp_0033 INTO ls_tmp_0033.
    lv_sum_0033 = lv_sum_0033 + ls_tmp_0033-seatsocc.
    IF lv_sum_0033 > 1033.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0033', lv_sum_0033.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0034 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0034 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0034 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0034 TYPE sflight,
        lv_sum_0034 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0034
    WHERE carrid = iv_carrid
      AND seatsocc > 238.
  LOOP AT lt_tmp_0034 INTO ls_tmp_0034.
    lv_sum_0034 = lv_sum_0034 + ls_tmp_0034-seatsocc.
    IF lv_sum_0034 > 1034.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0034', lv_sum_0034.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0035 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0035 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0035 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0035 TYPE sflight,
        lv_sum_0035 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0035
    WHERE carrid = iv_carrid
      AND seatsocc > 245.
  LOOP AT lt_tmp_0035 INTO ls_tmp_0035.
    lv_sum_0035 = lv_sum_0035 + ls_tmp_0035-seatsocc.
    IF lv_sum_0035 > 1035.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0035', lv_sum_0035.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0036 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0036 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0036 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0036 TYPE sflight,
        lv_sum_0036 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0036
    WHERE carrid = iv_carrid
      AND seatsocc > 252.
  LOOP AT lt_tmp_0036 INTO ls_tmp_0036.
    lv_sum_0036 = lv_sum_0036 + ls_tmp_0036-seatsocc.
    IF lv_sum_0036 > 1036.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0036', lv_sum_0036.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0037 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0037 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0037 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0037 TYPE sflight,
        lv_sum_0037 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0037
    WHERE carrid = iv_carrid
      AND seatsocc > 259.
  LOOP AT lt_tmp_0037 INTO ls_tmp_0037.
    lv_sum_0037 = lv_sum_0037 + ls_tmp_0037-seatsocc.
    IF lv_sum_0037 > 1037.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0037', lv_sum_0037.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0038 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0038 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0038 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0038 TYPE sflight,
        lv_sum_0038 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0038
    WHERE carrid = iv_carrid
      AND seatsocc > 266.
  LOOP AT lt_tmp_0038 INTO ls_tmp_0038.
    lv_sum_0038 = lv_sum_0038 + ls_tmp_0038-seatsocc.
    IF lv_sum_0038 > 1038.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0038', lv_sum_0038.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0039 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0039 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0039 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0039 TYPE sflight,
        lv_sum_0039 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0039
    WHERE carrid = iv_carrid
      AND seatsocc > 273.
  LOOP AT lt_tmp_0039 INTO ls_tmp_0039.
    lv_sum_0039 = lv_sum_0039 + ls_tmp_0039-seatsocc.
    IF lv_sum_0039 > 1039.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0039', lv_sum_0039.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0040 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0040 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0040 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0040 TYPE sflight,
        lv_sum_0040 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0040
    WHERE carrid = iv_carrid
      AND seatsocc > 280.
  LOOP AT lt_tmp_0040 INTO ls_tmp_0040.
    lv_sum_0040 = lv_sum_0040 + ls_tmp_0040-seatsocc.
    IF lv_sum_0040 > 1040.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0040', lv_sum_0040.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0041 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0041 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0041 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0041 TYPE sflight,
        lv_sum_0041 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0041
    WHERE carrid = iv_carrid
      AND seatsocc > 287.
  LOOP AT lt_tmp_0041 INTO ls_tmp_0041.
    lv_sum_0041 = lv_sum_0041 + ls_tmp_0041-seatsocc.
    IF lv_sum_0041 > 1041.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0041', lv_sum_0041.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0042 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0042 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0042 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0042 TYPE sflight,
        lv_sum_0042 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0042
    WHERE carrid = iv_carrid
      AND seatsocc > 294.
  LOOP AT lt_tmp_0042 INTO ls_tmp_0042.
    lv_sum_0042 = lv_sum_0042 + ls_tmp_0042-seatsocc.
    IF lv_sum_0042 > 1042.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0042', lv_sum_0042.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0043 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0043 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0043 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0043 TYPE sflight,
        lv_sum_0043 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0043
    WHERE carrid = iv_carrid
      AND seatsocc > 1.
  LOOP AT lt_tmp_0043 INTO ls_tmp_0043.
    lv_sum_0043 = lv_sum_0043 + ls_tmp_0043-seatsocc.
    IF lv_sum_0043 > 1043.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0043', lv_sum_0043.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0044 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0044 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0044 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0044 TYPE sflight,
        lv_sum_0044 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0044
    WHERE carrid = iv_carrid
      AND seatsocc > 8.
  LOOP AT lt_tmp_0044 INTO ls_tmp_0044.
    lv_sum_0044 = lv_sum_0044 + ls_tmp_0044-seatsocc.
    IF lv_sum_0044 > 1044.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0044', lv_sum_0044.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0045 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0045 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0045 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0045 TYPE sflight,
        lv_sum_0045 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0045
    WHERE carrid = iv_carrid
      AND seatsocc > 15.
  LOOP AT lt_tmp_0045 INTO ls_tmp_0045.
    lv_sum_0045 = lv_sum_0045 + ls_tmp_0045-seatsocc.
    IF lv_sum_0045 > 1045.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0045', lv_sum_0045.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0046 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0046 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0046 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0046 TYPE sflight,
        lv_sum_0046 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0046
    WHERE carrid = iv_carrid
      AND seatsocc > 22.
  LOOP AT lt_tmp_0046 INTO ls_tmp_0046.
    lv_sum_0046 = lv_sum_0046 + ls_tmp_0046-seatsocc.
    IF lv_sum_0046 > 1046.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0046', lv_sum_0046.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0047 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0047 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0047 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0047 TYPE sflight,
        lv_sum_0047 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0047
    WHERE carrid = iv_carrid
      AND seatsocc > 29.
  LOOP AT lt_tmp_0047 INTO ls_tmp_0047.
    lv_sum_0047 = lv_sum_0047 + ls_tmp_0047-seatsocc.
    IF lv_sum_0047 > 1047.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0047', lv_sum_0047.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0048 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0048 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0048 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0048 TYPE sflight,
        lv_sum_0048 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0048
    WHERE carrid = iv_carrid
      AND seatsocc > 36.
  LOOP AT lt_tmp_0048 INTO ls_tmp_0048.
    lv_sum_0048 = lv_sum_0048 + ls_tmp_0048-seatsocc.
    IF lv_sum_0048 > 1048.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0048', lv_sum_0048.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0049 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0049 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0049 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0049 TYPE sflight,
        lv_sum_0049 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0049
    WHERE carrid = iv_carrid
      AND seatsocc > 43.
  LOOP AT lt_tmp_0049 INTO ls_tmp_0049.
    lv_sum_0049 = lv_sum_0049 + ls_tmp_0049-seatsocc.
    IF lv_sum_0049 > 1049.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0049', lv_sum_0049.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0050 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0050 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0050 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0050 TYPE sflight,
        lv_sum_0050 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0050
    WHERE carrid = iv_carrid
      AND seatsocc > 50.
  LOOP AT lt_tmp_0050 INTO ls_tmp_0050.
    lv_sum_0050 = lv_sum_0050 + ls_tmp_0050-seatsocc.
    IF lv_sum_0050 > 1050.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0050', lv_sum_0050.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0051 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0051 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0051 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0051 TYPE sflight,
        lv_sum_0051 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0051
    WHERE carrid = iv_carrid
      AND seatsocc > 57.
  LOOP AT lt_tmp_0051 INTO ls_tmp_0051.
    lv_sum_0051 = lv_sum_0051 + ls_tmp_0051-seatsocc.
    IF lv_sum_0051 > 1051.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0051', lv_sum_0051.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0052 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0052 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0052 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0052 TYPE sflight,
        lv_sum_0052 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0052
    WHERE carrid = iv_carrid
      AND seatsocc > 64.
  LOOP AT lt_tmp_0052 INTO ls_tmp_0052.
    lv_sum_0052 = lv_sum_0052 + ls_tmp_0052-seatsocc.
    IF lv_sum_0052 > 1052.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0052', lv_sum_0052.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0053 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0053 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0053 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0053 TYPE sflight,
        lv_sum_0053 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0053
    WHERE carrid = iv_carrid
      AND seatsocc > 71.
  LOOP AT lt_tmp_0053 INTO ls_tmp_0053.
    lv_sum_0053 = lv_sum_0053 + ls_tmp_0053-seatsocc.
    IF lv_sum_0053 > 1053.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0053', lv_sum_0053.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0054 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0054 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0054 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0054 TYPE sflight,
        lv_sum_0054 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0054
    WHERE carrid = iv_carrid
      AND seatsocc > 78.
  LOOP AT lt_tmp_0054 INTO ls_tmp_0054.
    lv_sum_0054 = lv_sum_0054 + ls_tmp_0054-seatsocc.
    IF lv_sum_0054 > 1054.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0054', lv_sum_0054.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0055 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0055 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0055 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0055 TYPE sflight,
        lv_sum_0055 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0055
    WHERE carrid = iv_carrid
      AND seatsocc > 85.
  LOOP AT lt_tmp_0055 INTO ls_tmp_0055.
    lv_sum_0055 = lv_sum_0055 + ls_tmp_0055-seatsocc.
    IF lv_sum_0055 > 1055.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0055', lv_sum_0055.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0056 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0056 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0056 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0056 TYPE sflight,
        lv_sum_0056 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0056
    WHERE carrid = iv_carrid
      AND seatsocc > 92.
  LOOP AT lt_tmp_0056 INTO ls_tmp_0056.
    lv_sum_0056 = lv_sum_0056 + ls_tmp_0056-seatsocc.
    IF lv_sum_0056 > 1056.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0056', lv_sum_0056.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0057 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0057 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0057 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0057 TYPE sflight,
        lv_sum_0057 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0057
    WHERE carrid = iv_carrid
      AND seatsocc > 99.
  LOOP AT lt_tmp_0057 INTO ls_tmp_0057.
    lv_sum_0057 = lv_sum_0057 + ls_tmp_0057-seatsocc.
    IF lv_sum_0057 > 1057.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0057', lv_sum_0057.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0058 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0058 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0058 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0058 TYPE sflight,
        lv_sum_0058 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0058
    WHERE carrid = iv_carrid
      AND seatsocc > 106.
  LOOP AT lt_tmp_0058 INTO ls_tmp_0058.
    lv_sum_0058 = lv_sum_0058 + ls_tmp_0058-seatsocc.
    IF lv_sum_0058 > 1058.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0058', lv_sum_0058.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0059 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0059 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0059 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0059 TYPE sflight,
        lv_sum_0059 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0059
    WHERE carrid = iv_carrid
      AND seatsocc > 113.
  LOOP AT lt_tmp_0059 INTO ls_tmp_0059.
    lv_sum_0059 = lv_sum_0059 + ls_tmp_0059-seatsocc.
    IF lv_sum_0059 > 1059.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0059', lv_sum_0059.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0060 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0060 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0060 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0060 TYPE sflight,
        lv_sum_0060 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0060
    WHERE carrid = iv_carrid
      AND seatsocc > 120.
  LOOP AT lt_tmp_0060 INTO ls_tmp_0060.
    lv_sum_0060 = lv_sum_0060 + ls_tmp_0060-seatsocc.
    IF lv_sum_0060 > 1060.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0060', lv_sum_0060.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0061 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0061 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0061 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0061 TYPE sflight,
        lv_sum_0061 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0061
    WHERE carrid = iv_carrid
      AND seatsocc > 127.
  LOOP AT lt_tmp_0061 INTO ls_tmp_0061.
    lv_sum_0061 = lv_sum_0061 + ls_tmp_0061-seatsocc.
    IF lv_sum_0061 > 1061.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0061', lv_sum_0061.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0062 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0062 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0062 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0062 TYPE sflight,
        lv_sum_0062 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0062
    WHERE carrid = iv_carrid
      AND seatsocc > 134.
  LOOP AT lt_tmp_0062 INTO ls_tmp_0062.
    lv_sum_0062 = lv_sum_0062 + ls_tmp_0062-seatsocc.
    IF lv_sum_0062 > 1062.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0062', lv_sum_0062.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0063 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0063 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0063 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0063 TYPE sflight,
        lv_sum_0063 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0063
    WHERE carrid = iv_carrid
      AND seatsocc > 141.
  LOOP AT lt_tmp_0063 INTO ls_tmp_0063.
    lv_sum_0063 = lv_sum_0063 + ls_tmp_0063-seatsocc.
    IF lv_sum_0063 > 1063.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0063', lv_sum_0063.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0064 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0064 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0064 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0064 TYPE sflight,
        lv_sum_0064 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0064
    WHERE carrid = iv_carrid
      AND seatsocc > 148.
  LOOP AT lt_tmp_0064 INTO ls_tmp_0064.
    lv_sum_0064 = lv_sum_0064 + ls_tmp_0064-seatsocc.
    IF lv_sum_0064 > 1064.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0064', lv_sum_0064.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0065 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0065 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0065 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0065 TYPE sflight,
        lv_sum_0065 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0065
    WHERE carrid = iv_carrid
      AND seatsocc > 155.
  LOOP AT lt_tmp_0065 INTO ls_tmp_0065.
    lv_sum_0065 = lv_sum_0065 + ls_tmp_0065-seatsocc.
    IF lv_sum_0065 > 1065.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0065', lv_sum_0065.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0066 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0066 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0066 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0066 TYPE sflight,
        lv_sum_0066 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0066
    WHERE carrid = iv_carrid
      AND seatsocc > 162.
  LOOP AT lt_tmp_0066 INTO ls_tmp_0066.
    lv_sum_0066 = lv_sum_0066 + ls_tmp_0066-seatsocc.
    IF lv_sum_0066 > 1066.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0066', lv_sum_0066.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0067 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0067 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0067 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0067 TYPE sflight,
        lv_sum_0067 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0067
    WHERE carrid = iv_carrid
      AND seatsocc > 169.
  LOOP AT lt_tmp_0067 INTO ls_tmp_0067.
    lv_sum_0067 = lv_sum_0067 + ls_tmp_0067-seatsocc.
    IF lv_sum_0067 > 1067.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0067', lv_sum_0067.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0068 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0068 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0068 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0068 TYPE sflight,
        lv_sum_0068 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0068
    WHERE carrid = iv_carrid
      AND seatsocc > 176.
  LOOP AT lt_tmp_0068 INTO ls_tmp_0068.
    lv_sum_0068 = lv_sum_0068 + ls_tmp_0068-seatsocc.
    IF lv_sum_0068 > 1068.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0068', lv_sum_0068.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0069 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0069 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0069 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0069 TYPE sflight,
        lv_sum_0069 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0069
    WHERE carrid = iv_carrid
      AND seatsocc > 183.
  LOOP AT lt_tmp_0069 INTO ls_tmp_0069.
    lv_sum_0069 = lv_sum_0069 + ls_tmp_0069-seatsocc.
    IF lv_sum_0069 > 1069.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0069', lv_sum_0069.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0070 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0070 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0070 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0070 TYPE sflight,
        lv_sum_0070 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0070
    WHERE carrid = iv_carrid
      AND seatsocc > 190.
  LOOP AT lt_tmp_0070 INTO ls_tmp_0070.
    lv_sum_0070 = lv_sum_0070 + ls_tmp_0070-seatsocc.
    IF lv_sum_0070 > 1070.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0070', lv_sum_0070.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0071 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0071 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0071 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0071 TYPE sflight,
        lv_sum_0071 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0071
    WHERE carrid = iv_carrid
      AND seatsocc > 197.
  LOOP AT lt_tmp_0071 INTO ls_tmp_0071.
    lv_sum_0071 = lv_sum_0071 + ls_tmp_0071-seatsocc.
    IF lv_sum_0071 > 1071.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0071', lv_sum_0071.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0072 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0072 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0072 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0072 TYPE sflight,
        lv_sum_0072 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0072
    WHERE carrid = iv_carrid
      AND seatsocc > 204.
  LOOP AT lt_tmp_0072 INTO ls_tmp_0072.
    lv_sum_0072 = lv_sum_0072 + ls_tmp_0072-seatsocc.
    IF lv_sum_0072 > 1072.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0072', lv_sum_0072.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0073 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0073 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0073 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0073 TYPE sflight,
        lv_sum_0073 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0073
    WHERE carrid = iv_carrid
      AND seatsocc > 211.
  LOOP AT lt_tmp_0073 INTO ls_tmp_0073.
    lv_sum_0073 = lv_sum_0073 + ls_tmp_0073-seatsocc.
    IF lv_sum_0073 > 1073.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0073', lv_sum_0073.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0074 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0074 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0074 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0074 TYPE sflight,
        lv_sum_0074 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0074
    WHERE carrid = iv_carrid
      AND seatsocc > 218.
  LOOP AT lt_tmp_0074 INTO ls_tmp_0074.
    lv_sum_0074 = lv_sum_0074 + ls_tmp_0074-seatsocc.
    IF lv_sum_0074 > 1074.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0074', lv_sum_0074.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0075 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0075 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0075 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0075 TYPE sflight,
        lv_sum_0075 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0075
    WHERE carrid = iv_carrid
      AND seatsocc > 225.
  LOOP AT lt_tmp_0075 INTO ls_tmp_0075.
    lv_sum_0075 = lv_sum_0075 + ls_tmp_0075-seatsocc.
    IF lv_sum_0075 > 1075.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0075', lv_sum_0075.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0076 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0076 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0076 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0076 TYPE sflight,
        lv_sum_0076 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0076
    WHERE carrid = iv_carrid
      AND seatsocc > 232.
  LOOP AT lt_tmp_0076 INTO ls_tmp_0076.
    lv_sum_0076 = lv_sum_0076 + ls_tmp_0076-seatsocc.
    IF lv_sum_0076 > 1076.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0076', lv_sum_0076.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0077 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0077 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0077 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0077 TYPE sflight,
        lv_sum_0077 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0077
    WHERE carrid = iv_carrid
      AND seatsocc > 239.
  LOOP AT lt_tmp_0077 INTO ls_tmp_0077.
    lv_sum_0077 = lv_sum_0077 + ls_tmp_0077-seatsocc.
    IF lv_sum_0077 > 1077.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0077', lv_sum_0077.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0078 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0078 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0078 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0078 TYPE sflight,
        lv_sum_0078 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0078
    WHERE carrid = iv_carrid
      AND seatsocc > 246.
  LOOP AT lt_tmp_0078 INTO ls_tmp_0078.
    lv_sum_0078 = lv_sum_0078 + ls_tmp_0078-seatsocc.
    IF lv_sum_0078 > 1078.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0078', lv_sum_0078.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0079 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0079 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0079 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0079 TYPE sflight,
        lv_sum_0079 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0079
    WHERE carrid = iv_carrid
      AND seatsocc > 253.
  LOOP AT lt_tmp_0079 INTO ls_tmp_0079.
    lv_sum_0079 = lv_sum_0079 + ls_tmp_0079-seatsocc.
    IF lv_sum_0079 > 1079.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0079', lv_sum_0079.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0080 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0080 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0080 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0080 TYPE sflight,
        lv_sum_0080 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0080
    WHERE carrid = iv_carrid
      AND seatsocc > 260.
  LOOP AT lt_tmp_0080 INTO ls_tmp_0080.
    lv_sum_0080 = lv_sum_0080 + ls_tmp_0080-seatsocc.
    IF lv_sum_0080 > 1080.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0080', lv_sum_0080.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0081 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0081 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0081 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0081 TYPE sflight,
        lv_sum_0081 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0081
    WHERE carrid = iv_carrid
      AND seatsocc > 267.
  LOOP AT lt_tmp_0081 INTO ls_tmp_0081.
    lv_sum_0081 = lv_sum_0081 + ls_tmp_0081-seatsocc.
    IF lv_sum_0081 > 1081.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0081', lv_sum_0081.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0082 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0082 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0082 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0082 TYPE sflight,
        lv_sum_0082 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0082
    WHERE carrid = iv_carrid
      AND seatsocc > 274.
  LOOP AT lt_tmp_0082 INTO ls_tmp_0082.
    lv_sum_0082 = lv_sum_0082 + ls_tmp_0082-seatsocc.
    IF lv_sum_0082 > 1082.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0082', lv_sum_0082.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0083 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0083 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0083 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0083 TYPE sflight,
        lv_sum_0083 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0083
    WHERE carrid = iv_carrid
      AND seatsocc > 281.
  LOOP AT lt_tmp_0083 INTO ls_tmp_0083.
    lv_sum_0083 = lv_sum_0083 + ls_tmp_0083-seatsocc.
    IF lv_sum_0083 > 1083.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0083', lv_sum_0083.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0084 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0084 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0084 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0084 TYPE sflight,
        lv_sum_0084 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0084
    WHERE carrid = iv_carrid
      AND seatsocc > 288.
  LOOP AT lt_tmp_0084 INTO ls_tmp_0084.
    lv_sum_0084 = lv_sum_0084 + ls_tmp_0084-seatsocc.
    IF lv_sum_0084 > 1084.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0084', lv_sum_0084.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0085 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0085 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0085 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0085 TYPE sflight,
        lv_sum_0085 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0085
    WHERE carrid = iv_carrid
      AND seatsocc > 295.
  LOOP AT lt_tmp_0085 INTO ls_tmp_0085.
    lv_sum_0085 = lv_sum_0085 + ls_tmp_0085-seatsocc.
    IF lv_sum_0085 > 1085.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0085', lv_sum_0085.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0086 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0086 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0086 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0086 TYPE sflight,
        lv_sum_0086 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0086
    WHERE carrid = iv_carrid
      AND seatsocc > 2.
  LOOP AT lt_tmp_0086 INTO ls_tmp_0086.
    lv_sum_0086 = lv_sum_0086 + ls_tmp_0086-seatsocc.
    IF lv_sum_0086 > 1086.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0086', lv_sum_0086.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0087 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0087 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0087 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0087 TYPE sflight,
        lv_sum_0087 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0087
    WHERE carrid = iv_carrid
      AND seatsocc > 9.
  LOOP AT lt_tmp_0087 INTO ls_tmp_0087.
    lv_sum_0087 = lv_sum_0087 + ls_tmp_0087-seatsocc.
    IF lv_sum_0087 > 1087.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0087', lv_sum_0087.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0088 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0088 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0088 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0088 TYPE sflight,
        lv_sum_0088 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0088
    WHERE carrid = iv_carrid
      AND seatsocc > 16.
  LOOP AT lt_tmp_0088 INTO ls_tmp_0088.
    lv_sum_0088 = lv_sum_0088 + ls_tmp_0088-seatsocc.
    IF lv_sum_0088 > 1088.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0088', lv_sum_0088.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0089 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0089 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0089 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0089 TYPE sflight,
        lv_sum_0089 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0089
    WHERE carrid = iv_carrid
      AND seatsocc > 23.
  LOOP AT lt_tmp_0089 INTO ls_tmp_0089.
    lv_sum_0089 = lv_sum_0089 + ls_tmp_0089-seatsocc.
    IF lv_sum_0089 > 1089.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0089', lv_sum_0089.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0090 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0090 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0090 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0090 TYPE sflight,
        lv_sum_0090 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0090
    WHERE carrid = iv_carrid
      AND seatsocc > 30.
  LOOP AT lt_tmp_0090 INTO ls_tmp_0090.
    lv_sum_0090 = lv_sum_0090 + ls_tmp_0090-seatsocc.
    IF lv_sum_0090 > 1090.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0090', lv_sum_0090.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0091 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0091 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0091 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0091 TYPE sflight,
        lv_sum_0091 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0091
    WHERE carrid = iv_carrid
      AND seatsocc > 37.
  LOOP AT lt_tmp_0091 INTO ls_tmp_0091.
    lv_sum_0091 = lv_sum_0091 + ls_tmp_0091-seatsocc.
    IF lv_sum_0091 > 1091.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0091', lv_sum_0091.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0092 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0092 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0092 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0092 TYPE sflight,
        lv_sum_0092 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0092
    WHERE carrid = iv_carrid
      AND seatsocc > 44.
  LOOP AT lt_tmp_0092 INTO ls_tmp_0092.
    lv_sum_0092 = lv_sum_0092 + ls_tmp_0092-seatsocc.
    IF lv_sum_0092 > 1092.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0092', lv_sum_0092.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0093 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0093 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0093 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0093 TYPE sflight,
        lv_sum_0093 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0093
    WHERE carrid = iv_carrid
      AND seatsocc > 51.
  LOOP AT lt_tmp_0093 INTO ls_tmp_0093.
    lv_sum_0093 = lv_sum_0093 + ls_tmp_0093-seatsocc.
    IF lv_sum_0093 > 1093.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0093', lv_sum_0093.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0094 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0094 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0094 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0094 TYPE sflight,
        lv_sum_0094 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0094
    WHERE carrid = iv_carrid
      AND seatsocc > 58.
  LOOP AT lt_tmp_0094 INTO ls_tmp_0094.
    lv_sum_0094 = lv_sum_0094 + ls_tmp_0094-seatsocc.
    IF lv_sum_0094 > 1094.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0094', lv_sum_0094.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0095 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0095 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0095 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0095 TYPE sflight,
        lv_sum_0095 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0095
    WHERE carrid = iv_carrid
      AND seatsocc > 65.
  LOOP AT lt_tmp_0095 INTO ls_tmp_0095.
    lv_sum_0095 = lv_sum_0095 + ls_tmp_0095-seatsocc.
    IF lv_sum_0095 > 1095.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0095', lv_sum_0095.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0096 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0096 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0096 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0096 TYPE sflight,
        lv_sum_0096 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0096
    WHERE carrid = iv_carrid
      AND seatsocc > 72.
  LOOP AT lt_tmp_0096 INTO ls_tmp_0096.
    lv_sum_0096 = lv_sum_0096 + ls_tmp_0096-seatsocc.
    IF lv_sum_0096 > 1096.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0096', lv_sum_0096.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0097 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0097 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0097 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0097 TYPE sflight,
        lv_sum_0097 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0097
    WHERE carrid = iv_carrid
      AND seatsocc > 79.
  LOOP AT lt_tmp_0097 INTO ls_tmp_0097.
    lv_sum_0097 = lv_sum_0097 + ls_tmp_0097-seatsocc.
    IF lv_sum_0097 > 1097.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0097', lv_sum_0097.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0098 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0098 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0098 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0098 TYPE sflight,
        lv_sum_0098 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0098
    WHERE carrid = iv_carrid
      AND seatsocc > 86.
  LOOP AT lt_tmp_0098 INTO ls_tmp_0098.
    lv_sum_0098 = lv_sum_0098 + ls_tmp_0098-seatsocc.
    IF lv_sum_0098 > 1098.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0098', lv_sum_0098.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0099 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0099 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0099 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0099 TYPE sflight,
        lv_sum_0099 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0099
    WHERE carrid = iv_carrid
      AND seatsocc > 93.
  LOOP AT lt_tmp_0099 INTO ls_tmp_0099.
    lv_sum_0099 = lv_sum_0099 + ls_tmp_0099-seatsocc.
    IF lv_sum_0099 > 1099.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0099', lv_sum_0099.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0100 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0100 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0100 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0100 TYPE sflight,
        lv_sum_0100 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0100
    WHERE carrid = iv_carrid
      AND seatsocc > 100.
  LOOP AT lt_tmp_0100 INTO ls_tmp_0100.
    lv_sum_0100 = lv_sum_0100 + ls_tmp_0100-seatsocc.
    IF lv_sum_0100 > 1100.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0100', lv_sum_0100.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0101 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0101 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0101 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0101 TYPE sflight,
        lv_sum_0101 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0101
    WHERE carrid = iv_carrid
      AND seatsocc > 107.
  LOOP AT lt_tmp_0101 INTO ls_tmp_0101.
    lv_sum_0101 = lv_sum_0101 + ls_tmp_0101-seatsocc.
    IF lv_sum_0101 > 1101.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0101', lv_sum_0101.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0102 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0102 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0102 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0102 TYPE sflight,
        lv_sum_0102 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0102
    WHERE carrid = iv_carrid
      AND seatsocc > 114.
  LOOP AT lt_tmp_0102 INTO ls_tmp_0102.
    lv_sum_0102 = lv_sum_0102 + ls_tmp_0102-seatsocc.
    IF lv_sum_0102 > 1102.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0102', lv_sum_0102.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0103 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0103 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0103 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0103 TYPE sflight,
        lv_sum_0103 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0103
    WHERE carrid = iv_carrid
      AND seatsocc > 121.
  LOOP AT lt_tmp_0103 INTO ls_tmp_0103.
    lv_sum_0103 = lv_sum_0103 + ls_tmp_0103-seatsocc.
    IF lv_sum_0103 > 1103.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0103', lv_sum_0103.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0104 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0104 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0104 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0104 TYPE sflight,
        lv_sum_0104 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0104
    WHERE carrid = iv_carrid
      AND seatsocc > 128.
  LOOP AT lt_tmp_0104 INTO ls_tmp_0104.
    lv_sum_0104 = lv_sum_0104 + ls_tmp_0104-seatsocc.
    IF lv_sum_0104 > 1104.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0104', lv_sum_0104.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0105 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0105 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0105 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0105 TYPE sflight,
        lv_sum_0105 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0105
    WHERE carrid = iv_carrid
      AND seatsocc > 135.
  LOOP AT lt_tmp_0105 INTO ls_tmp_0105.
    lv_sum_0105 = lv_sum_0105 + ls_tmp_0105-seatsocc.
    IF lv_sum_0105 > 1105.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0105', lv_sum_0105.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0106 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0106 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0106 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0106 TYPE sflight,
        lv_sum_0106 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0106
    WHERE carrid = iv_carrid
      AND seatsocc > 142.
  LOOP AT lt_tmp_0106 INTO ls_tmp_0106.
    lv_sum_0106 = lv_sum_0106 + ls_tmp_0106-seatsocc.
    IF lv_sum_0106 > 1106.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0106', lv_sum_0106.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0107 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0107 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0107 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0107 TYPE sflight,
        lv_sum_0107 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0107
    WHERE carrid = iv_carrid
      AND seatsocc > 149.
  LOOP AT lt_tmp_0107 INTO ls_tmp_0107.
    lv_sum_0107 = lv_sum_0107 + ls_tmp_0107-seatsocc.
    IF lv_sum_0107 > 1107.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0107', lv_sum_0107.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0108 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0108 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0108 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0108 TYPE sflight,
        lv_sum_0108 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0108
    WHERE carrid = iv_carrid
      AND seatsocc > 156.
  LOOP AT lt_tmp_0108 INTO ls_tmp_0108.
    lv_sum_0108 = lv_sum_0108 + ls_tmp_0108-seatsocc.
    IF lv_sum_0108 > 1108.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0108', lv_sum_0108.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0109 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0109 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0109 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0109 TYPE sflight,
        lv_sum_0109 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0109
    WHERE carrid = iv_carrid
      AND seatsocc > 163.
  LOOP AT lt_tmp_0109 INTO ls_tmp_0109.
    lv_sum_0109 = lv_sum_0109 + ls_tmp_0109-seatsocc.
    IF lv_sum_0109 > 1109.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0109', lv_sum_0109.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0110 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0110 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0110 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0110 TYPE sflight,
        lv_sum_0110 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0110
    WHERE carrid = iv_carrid
      AND seatsocc > 170.
  LOOP AT lt_tmp_0110 INTO ls_tmp_0110.
    lv_sum_0110 = lv_sum_0110 + ls_tmp_0110-seatsocc.
    IF lv_sum_0110 > 1110.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0110', lv_sum_0110.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0111 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0111 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0111 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0111 TYPE sflight,
        lv_sum_0111 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0111
    WHERE carrid = iv_carrid
      AND seatsocc > 177.
  LOOP AT lt_tmp_0111 INTO ls_tmp_0111.
    lv_sum_0111 = lv_sum_0111 + ls_tmp_0111-seatsocc.
    IF lv_sum_0111 > 1111.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0111', lv_sum_0111.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0112 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0112 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0112 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0112 TYPE sflight,
        lv_sum_0112 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0112
    WHERE carrid = iv_carrid
      AND seatsocc > 184.
  LOOP AT lt_tmp_0112 INTO ls_tmp_0112.
    lv_sum_0112 = lv_sum_0112 + ls_tmp_0112-seatsocc.
    IF lv_sum_0112 > 1112.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0112', lv_sum_0112.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0113 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0113 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0113 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0113 TYPE sflight,
        lv_sum_0113 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0113
    WHERE carrid = iv_carrid
      AND seatsocc > 191.
  LOOP AT lt_tmp_0113 INTO ls_tmp_0113.
    lv_sum_0113 = lv_sum_0113 + ls_tmp_0113-seatsocc.
    IF lv_sum_0113 > 1113.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0113', lv_sum_0113.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0114 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0114 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0114 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0114 TYPE sflight,
        lv_sum_0114 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0114
    WHERE carrid = iv_carrid
      AND seatsocc > 198.
  LOOP AT lt_tmp_0114 INTO ls_tmp_0114.
    lv_sum_0114 = lv_sum_0114 + ls_tmp_0114-seatsocc.
    IF lv_sum_0114 > 1114.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0114', lv_sum_0114.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0115 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0115 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0115 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0115 TYPE sflight,
        lv_sum_0115 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0115
    WHERE carrid = iv_carrid
      AND seatsocc > 205.
  LOOP AT lt_tmp_0115 INTO ls_tmp_0115.
    lv_sum_0115 = lv_sum_0115 + ls_tmp_0115-seatsocc.
    IF lv_sum_0115 > 1115.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0115', lv_sum_0115.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0116 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0116 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0116 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0116 TYPE sflight,
        lv_sum_0116 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0116
    WHERE carrid = iv_carrid
      AND seatsocc > 212.
  LOOP AT lt_tmp_0116 INTO ls_tmp_0116.
    lv_sum_0116 = lv_sum_0116 + ls_tmp_0116-seatsocc.
    IF lv_sum_0116 > 1116.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0116', lv_sum_0116.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0117 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0117 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0117 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0117 TYPE sflight,
        lv_sum_0117 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0117
    WHERE carrid = iv_carrid
      AND seatsocc > 219.
  LOOP AT lt_tmp_0117 INTO ls_tmp_0117.
    lv_sum_0117 = lv_sum_0117 + ls_tmp_0117-seatsocc.
    IF lv_sum_0117 > 1117.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0117', lv_sum_0117.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0118 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0118 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0118 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0118 TYPE sflight,
        lv_sum_0118 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0118
    WHERE carrid = iv_carrid
      AND seatsocc > 226.
  LOOP AT lt_tmp_0118 INTO ls_tmp_0118.
    lv_sum_0118 = lv_sum_0118 + ls_tmp_0118-seatsocc.
    IF lv_sum_0118 > 1118.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0118', lv_sum_0118.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0119 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0119 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0119 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0119 TYPE sflight,
        lv_sum_0119 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0119
    WHERE carrid = iv_carrid
      AND seatsocc > 233.
  LOOP AT lt_tmp_0119 INTO ls_tmp_0119.
    lv_sum_0119 = lv_sum_0119 + ls_tmp_0119-seatsocc.
    IF lv_sum_0119 > 1119.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0119', lv_sum_0119.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0120 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0120 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0120 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0120 TYPE sflight,
        lv_sum_0120 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0120
    WHERE carrid = iv_carrid
      AND seatsocc > 240.
  LOOP AT lt_tmp_0120 INTO ls_tmp_0120.
    lv_sum_0120 = lv_sum_0120 + ls_tmp_0120-seatsocc.
    IF lv_sum_0120 > 1120.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0120', lv_sum_0120.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0121 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0121 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0121 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0121 TYPE sflight,
        lv_sum_0121 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0121
    WHERE carrid = iv_carrid
      AND seatsocc > 247.
  LOOP AT lt_tmp_0121 INTO ls_tmp_0121.
    lv_sum_0121 = lv_sum_0121 + ls_tmp_0121-seatsocc.
    IF lv_sum_0121 > 1121.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0121', lv_sum_0121.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0122 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0122 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0122 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0122 TYPE sflight,
        lv_sum_0122 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0122
    WHERE carrid = iv_carrid
      AND seatsocc > 254.
  LOOP AT lt_tmp_0122 INTO ls_tmp_0122.
    lv_sum_0122 = lv_sum_0122 + ls_tmp_0122-seatsocc.
    IF lv_sum_0122 > 1122.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0122', lv_sum_0122.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0123 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0123 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0123 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0123 TYPE sflight,
        lv_sum_0123 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0123
    WHERE carrid = iv_carrid
      AND seatsocc > 261.
  LOOP AT lt_tmp_0123 INTO ls_tmp_0123.
    lv_sum_0123 = lv_sum_0123 + ls_tmp_0123-seatsocc.
    IF lv_sum_0123 > 1123.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0123', lv_sum_0123.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0124 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0124 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0124 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0124 TYPE sflight,
        lv_sum_0124 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0124
    WHERE carrid = iv_carrid
      AND seatsocc > 268.
  LOOP AT lt_tmp_0124 INTO ls_tmp_0124.
    lv_sum_0124 = lv_sum_0124 + ls_tmp_0124-seatsocc.
    IF lv_sum_0124 > 1124.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0124', lv_sum_0124.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0125 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0125 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0125 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0125 TYPE sflight,
        lv_sum_0125 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0125
    WHERE carrid = iv_carrid
      AND seatsocc > 275.
  LOOP AT lt_tmp_0125 INTO ls_tmp_0125.
    lv_sum_0125 = lv_sum_0125 + ls_tmp_0125-seatsocc.
    IF lv_sum_0125 > 1125.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0125', lv_sum_0125.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0126 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0126 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0126 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0126 TYPE sflight,
        lv_sum_0126 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0126
    WHERE carrid = iv_carrid
      AND seatsocc > 282.
  LOOP AT lt_tmp_0126 INTO ls_tmp_0126.
    lv_sum_0126 = lv_sum_0126 + ls_tmp_0126-seatsocc.
    IF lv_sum_0126 > 1126.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0126', lv_sum_0126.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0127 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0127 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0127 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0127 TYPE sflight,
        lv_sum_0127 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0127
    WHERE carrid = iv_carrid
      AND seatsocc > 289.
  LOOP AT lt_tmp_0127 INTO ls_tmp_0127.
    lv_sum_0127 = lv_sum_0127 + ls_tmp_0127-seatsocc.
    IF lv_sum_0127 > 1127.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0127', lv_sum_0127.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0128 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0128 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0128 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0128 TYPE sflight,
        lv_sum_0128 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0128
    WHERE carrid = iv_carrid
      AND seatsocc > 296.
  LOOP AT lt_tmp_0128 INTO ls_tmp_0128.
    lv_sum_0128 = lv_sum_0128 + ls_tmp_0128-seatsocc.
    IF lv_sum_0128 > 1128.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0128', lv_sum_0128.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0129 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0129 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0129 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0129 TYPE sflight,
        lv_sum_0129 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0129
    WHERE carrid = iv_carrid
      AND seatsocc > 3.
  LOOP AT lt_tmp_0129 INTO ls_tmp_0129.
    lv_sum_0129 = lv_sum_0129 + ls_tmp_0129-seatsocc.
    IF lv_sum_0129 > 1129.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0129', lv_sum_0129.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0130 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0130 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0130 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0130 TYPE sflight,
        lv_sum_0130 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0130
    WHERE carrid = iv_carrid
      AND seatsocc > 10.
  LOOP AT lt_tmp_0130 INTO ls_tmp_0130.
    lv_sum_0130 = lv_sum_0130 + ls_tmp_0130-seatsocc.
    IF lv_sum_0130 > 1130.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0130', lv_sum_0130.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0131 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0131 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0131 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0131 TYPE sflight,
        lv_sum_0131 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0131
    WHERE carrid = iv_carrid
      AND seatsocc > 17.
  LOOP AT lt_tmp_0131 INTO ls_tmp_0131.
    lv_sum_0131 = lv_sum_0131 + ls_tmp_0131-seatsocc.
    IF lv_sum_0131 > 1131.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0131', lv_sum_0131.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0132 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0132 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0132 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0132 TYPE sflight,
        lv_sum_0132 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0132
    WHERE carrid = iv_carrid
      AND seatsocc > 24.
  LOOP AT lt_tmp_0132 INTO ls_tmp_0132.
    lv_sum_0132 = lv_sum_0132 + ls_tmp_0132-seatsocc.
    IF lv_sum_0132 > 1132.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0132', lv_sum_0132.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0133 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0133 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0133 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0133 TYPE sflight,
        lv_sum_0133 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0133
    WHERE carrid = iv_carrid
      AND seatsocc > 31.
  LOOP AT lt_tmp_0133 INTO ls_tmp_0133.
    lv_sum_0133 = lv_sum_0133 + ls_tmp_0133-seatsocc.
    IF lv_sum_0133 > 1133.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0133', lv_sum_0133.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0134 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0134 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0134 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0134 TYPE sflight,
        lv_sum_0134 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0134
    WHERE carrid = iv_carrid
      AND seatsocc > 38.
  LOOP AT lt_tmp_0134 INTO ls_tmp_0134.
    lv_sum_0134 = lv_sum_0134 + ls_tmp_0134-seatsocc.
    IF lv_sum_0134 > 1134.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0134', lv_sum_0134.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0135 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0135 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0135 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0135 TYPE sflight,
        lv_sum_0135 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0135
    WHERE carrid = iv_carrid
      AND seatsocc > 45.
  LOOP AT lt_tmp_0135 INTO ls_tmp_0135.
    lv_sum_0135 = lv_sum_0135 + ls_tmp_0135-seatsocc.
    IF lv_sum_0135 > 1135.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0135', lv_sum_0135.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0136 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0136 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0136 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0136 TYPE sflight,
        lv_sum_0136 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0136
    WHERE carrid = iv_carrid
      AND seatsocc > 52.
  LOOP AT lt_tmp_0136 INTO ls_tmp_0136.
    lv_sum_0136 = lv_sum_0136 + ls_tmp_0136-seatsocc.
    IF lv_sum_0136 > 1136.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0136', lv_sum_0136.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0137 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0137 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0137 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0137 TYPE sflight,
        lv_sum_0137 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0137
    WHERE carrid = iv_carrid
      AND seatsocc > 59.
  LOOP AT lt_tmp_0137 INTO ls_tmp_0137.
    lv_sum_0137 = lv_sum_0137 + ls_tmp_0137-seatsocc.
    IF lv_sum_0137 > 1137.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0137', lv_sum_0137.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0138 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0138 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0138 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0138 TYPE sflight,
        lv_sum_0138 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0138
    WHERE carrid = iv_carrid
      AND seatsocc > 66.
  LOOP AT lt_tmp_0138 INTO ls_tmp_0138.
    lv_sum_0138 = lv_sum_0138 + ls_tmp_0138-seatsocc.
    IF lv_sum_0138 > 1138.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0138', lv_sum_0138.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0139 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0139 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0139 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0139 TYPE sflight,
        lv_sum_0139 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0139
    WHERE carrid = iv_carrid
      AND seatsocc > 73.
  LOOP AT lt_tmp_0139 INTO ls_tmp_0139.
    lv_sum_0139 = lv_sum_0139 + ls_tmp_0139-seatsocc.
    IF lv_sum_0139 > 1139.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0139', lv_sum_0139.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0140 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0140 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0140 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0140 TYPE sflight,
        lv_sum_0140 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0140
    WHERE carrid = iv_carrid
      AND seatsocc > 80.
  LOOP AT lt_tmp_0140 INTO ls_tmp_0140.
    lv_sum_0140 = lv_sum_0140 + ls_tmp_0140-seatsocc.
    IF lv_sum_0140 > 1140.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0140', lv_sum_0140.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0141 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0141 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0141 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0141 TYPE sflight,
        lv_sum_0141 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0141
    WHERE carrid = iv_carrid
      AND seatsocc > 87.
  LOOP AT lt_tmp_0141 INTO ls_tmp_0141.
    lv_sum_0141 = lv_sum_0141 + ls_tmp_0141-seatsocc.
    IF lv_sum_0141 > 1141.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0141', lv_sum_0141.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0142 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0142 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0142 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0142 TYPE sflight,
        lv_sum_0142 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0142
    WHERE carrid = iv_carrid
      AND seatsocc > 94.
  LOOP AT lt_tmp_0142 INTO ls_tmp_0142.
    lv_sum_0142 = lv_sum_0142 + ls_tmp_0142-seatsocc.
    IF lv_sum_0142 > 1142.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0142', lv_sum_0142.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0143 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0143 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0143 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0143 TYPE sflight,
        lv_sum_0143 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0143
    WHERE carrid = iv_carrid
      AND seatsocc > 101.
  LOOP AT lt_tmp_0143 INTO ls_tmp_0143.
    lv_sum_0143 = lv_sum_0143 + ls_tmp_0143-seatsocc.
    IF lv_sum_0143 > 1143.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0143', lv_sum_0143.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0144 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0144 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0144 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0144 TYPE sflight,
        lv_sum_0144 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0144
    WHERE carrid = iv_carrid
      AND seatsocc > 108.
  LOOP AT lt_tmp_0144 INTO ls_tmp_0144.
    lv_sum_0144 = lv_sum_0144 + ls_tmp_0144-seatsocc.
    IF lv_sum_0144 > 1144.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0144', lv_sum_0144.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0145 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0145 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0145 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0145 TYPE sflight,
        lv_sum_0145 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0145
    WHERE carrid = iv_carrid
      AND seatsocc > 115.
  LOOP AT lt_tmp_0145 INTO ls_tmp_0145.
    lv_sum_0145 = lv_sum_0145 + ls_tmp_0145-seatsocc.
    IF lv_sum_0145 > 1145.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0145', lv_sum_0145.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0146 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0146 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0146 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0146 TYPE sflight,
        lv_sum_0146 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0146
    WHERE carrid = iv_carrid
      AND seatsocc > 122.
  LOOP AT lt_tmp_0146 INTO ls_tmp_0146.
    lv_sum_0146 = lv_sum_0146 + ls_tmp_0146-seatsocc.
    IF lv_sum_0146 > 1146.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0146', lv_sum_0146.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0147 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0147 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0147 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0147 TYPE sflight,
        lv_sum_0147 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0147
    WHERE carrid = iv_carrid
      AND seatsocc > 129.
  LOOP AT lt_tmp_0147 INTO ls_tmp_0147.
    lv_sum_0147 = lv_sum_0147 + ls_tmp_0147-seatsocc.
    IF lv_sum_0147 > 1147.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0147', lv_sum_0147.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0148 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0148 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0148 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0148 TYPE sflight,
        lv_sum_0148 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0148
    WHERE carrid = iv_carrid
      AND seatsocc > 136.
  LOOP AT lt_tmp_0148 INTO ls_tmp_0148.
    lv_sum_0148 = lv_sum_0148 + ls_tmp_0148-seatsocc.
    IF lv_sum_0148 > 1148.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0148', lv_sum_0148.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0149 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0149 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0149 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0149 TYPE sflight,
        lv_sum_0149 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0149
    WHERE carrid = iv_carrid
      AND seatsocc > 143.
  LOOP AT lt_tmp_0149 INTO ls_tmp_0149.
    lv_sum_0149 = lv_sum_0149 + ls_tmp_0149-seatsocc.
    IF lv_sum_0149 > 1149.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0149', lv_sum_0149.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0150 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0150 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0150 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0150 TYPE sflight,
        lv_sum_0150 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0150
    WHERE carrid = iv_carrid
      AND seatsocc > 150.
  LOOP AT lt_tmp_0150 INTO ls_tmp_0150.
    lv_sum_0150 = lv_sum_0150 + ls_tmp_0150-seatsocc.
    IF lv_sum_0150 > 1150.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0150', lv_sum_0150.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0151 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0151 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0151 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0151 TYPE sflight,
        lv_sum_0151 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0151
    WHERE carrid = iv_carrid
      AND seatsocc > 157.
  LOOP AT lt_tmp_0151 INTO ls_tmp_0151.
    lv_sum_0151 = lv_sum_0151 + ls_tmp_0151-seatsocc.
    IF lv_sum_0151 > 1151.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0151', lv_sum_0151.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0152 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0152 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0152 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0152 TYPE sflight,
        lv_sum_0152 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0152
    WHERE carrid = iv_carrid
      AND seatsocc > 164.
  LOOP AT lt_tmp_0152 INTO ls_tmp_0152.
    lv_sum_0152 = lv_sum_0152 + ls_tmp_0152-seatsocc.
    IF lv_sum_0152 > 1152.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0152', lv_sum_0152.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0153 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0153 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0153 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0153 TYPE sflight,
        lv_sum_0153 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0153
    WHERE carrid = iv_carrid
      AND seatsocc > 171.
  LOOP AT lt_tmp_0153 INTO ls_tmp_0153.
    lv_sum_0153 = lv_sum_0153 + ls_tmp_0153-seatsocc.
    IF lv_sum_0153 > 1153.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0153', lv_sum_0153.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0154 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0154 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0154 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0154 TYPE sflight,
        lv_sum_0154 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0154
    WHERE carrid = iv_carrid
      AND seatsocc > 178.
  LOOP AT lt_tmp_0154 INTO ls_tmp_0154.
    lv_sum_0154 = lv_sum_0154 + ls_tmp_0154-seatsocc.
    IF lv_sum_0154 > 1154.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0154', lv_sum_0154.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0155 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0155 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0155 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0155 TYPE sflight,
        lv_sum_0155 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0155
    WHERE carrid = iv_carrid
      AND seatsocc > 185.
  LOOP AT lt_tmp_0155 INTO ls_tmp_0155.
    lv_sum_0155 = lv_sum_0155 + ls_tmp_0155-seatsocc.
    IF lv_sum_0155 > 1155.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0155', lv_sum_0155.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0156 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0156 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0156 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0156 TYPE sflight,
        lv_sum_0156 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0156
    WHERE carrid = iv_carrid
      AND seatsocc > 192.
  LOOP AT lt_tmp_0156 INTO ls_tmp_0156.
    lv_sum_0156 = lv_sum_0156 + ls_tmp_0156-seatsocc.
    IF lv_sum_0156 > 1156.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0156', lv_sum_0156.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0157 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0157 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0157 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0157 TYPE sflight,
        lv_sum_0157 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0157
    WHERE carrid = iv_carrid
      AND seatsocc > 199.
  LOOP AT lt_tmp_0157 INTO ls_tmp_0157.
    lv_sum_0157 = lv_sum_0157 + ls_tmp_0157-seatsocc.
    IF lv_sum_0157 > 1157.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0157', lv_sum_0157.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0158 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0158 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0158 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0158 TYPE sflight,
        lv_sum_0158 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0158
    WHERE carrid = iv_carrid
      AND seatsocc > 206.
  LOOP AT lt_tmp_0158 INTO ls_tmp_0158.
    lv_sum_0158 = lv_sum_0158 + ls_tmp_0158-seatsocc.
    IF lv_sum_0158 > 1158.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0158', lv_sum_0158.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0159 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0159 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0159 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0159 TYPE sflight,
        lv_sum_0159 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0159
    WHERE carrid = iv_carrid
      AND seatsocc > 213.
  LOOP AT lt_tmp_0159 INTO ls_tmp_0159.
    lv_sum_0159 = lv_sum_0159 + ls_tmp_0159-seatsocc.
    IF lv_sum_0159 > 1159.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0159', lv_sum_0159.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0160 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0160 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0160 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0160 TYPE sflight,
        lv_sum_0160 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0160
    WHERE carrid = iv_carrid
      AND seatsocc > 220.
  LOOP AT lt_tmp_0160 INTO ls_tmp_0160.
    lv_sum_0160 = lv_sum_0160 + ls_tmp_0160-seatsocc.
    IF lv_sum_0160 > 1160.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0160', lv_sum_0160.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0161 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0161 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0161 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0161 TYPE sflight,
        lv_sum_0161 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0161
    WHERE carrid = iv_carrid
      AND seatsocc > 227.
  LOOP AT lt_tmp_0161 INTO ls_tmp_0161.
    lv_sum_0161 = lv_sum_0161 + ls_tmp_0161-seatsocc.
    IF lv_sum_0161 > 1161.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0161', lv_sum_0161.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0162 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0162 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0162 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0162 TYPE sflight,
        lv_sum_0162 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0162
    WHERE carrid = iv_carrid
      AND seatsocc > 234.
  LOOP AT lt_tmp_0162 INTO ls_tmp_0162.
    lv_sum_0162 = lv_sum_0162 + ls_tmp_0162-seatsocc.
    IF lv_sum_0162 > 1162.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0162', lv_sum_0162.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0163 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0163 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0163 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0163 TYPE sflight,
        lv_sum_0163 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0163
    WHERE carrid = iv_carrid
      AND seatsocc > 241.
  LOOP AT lt_tmp_0163 INTO ls_tmp_0163.
    lv_sum_0163 = lv_sum_0163 + ls_tmp_0163-seatsocc.
    IF lv_sum_0163 > 1163.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0163', lv_sum_0163.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0164 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0164 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0164 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0164 TYPE sflight,
        lv_sum_0164 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0164
    WHERE carrid = iv_carrid
      AND seatsocc > 248.
  LOOP AT lt_tmp_0164 INTO ls_tmp_0164.
    lv_sum_0164 = lv_sum_0164 + ls_tmp_0164-seatsocc.
    IF lv_sum_0164 > 1164.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0164', lv_sum_0164.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0165 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0165 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0165 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0165 TYPE sflight,
        lv_sum_0165 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0165
    WHERE carrid = iv_carrid
      AND seatsocc > 255.
  LOOP AT lt_tmp_0165 INTO ls_tmp_0165.
    lv_sum_0165 = lv_sum_0165 + ls_tmp_0165-seatsocc.
    IF lv_sum_0165 > 1165.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0165', lv_sum_0165.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0166 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0166 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0166 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0166 TYPE sflight,
        lv_sum_0166 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0166
    WHERE carrid = iv_carrid
      AND seatsocc > 262.
  LOOP AT lt_tmp_0166 INTO ls_tmp_0166.
    lv_sum_0166 = lv_sum_0166 + ls_tmp_0166-seatsocc.
    IF lv_sum_0166 > 1166.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0166', lv_sum_0166.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0167 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0167 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0167 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0167 TYPE sflight,
        lv_sum_0167 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0167
    WHERE carrid = iv_carrid
      AND seatsocc > 269.
  LOOP AT lt_tmp_0167 INTO ls_tmp_0167.
    lv_sum_0167 = lv_sum_0167 + ls_tmp_0167-seatsocc.
    IF lv_sum_0167 > 1167.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0167', lv_sum_0167.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0168 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0168 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0168 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0168 TYPE sflight,
        lv_sum_0168 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0168
    WHERE carrid = iv_carrid
      AND seatsocc > 276.
  LOOP AT lt_tmp_0168 INTO ls_tmp_0168.
    lv_sum_0168 = lv_sum_0168 + ls_tmp_0168-seatsocc.
    IF lv_sum_0168 > 1168.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0168', lv_sum_0168.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0169 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0169 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0169 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0169 TYPE sflight,
        lv_sum_0169 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0169
    WHERE carrid = iv_carrid
      AND seatsocc > 283.
  LOOP AT lt_tmp_0169 INTO ls_tmp_0169.
    lv_sum_0169 = lv_sum_0169 + ls_tmp_0169-seatsocc.
    IF lv_sum_0169 > 1169.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0169', lv_sum_0169.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0170 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0170 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0170 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0170 TYPE sflight,
        lv_sum_0170 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0170
    WHERE carrid = iv_carrid
      AND seatsocc > 290.
  LOOP AT lt_tmp_0170 INTO ls_tmp_0170.
    lv_sum_0170 = lv_sum_0170 + ls_tmp_0170-seatsocc.
    IF lv_sum_0170 > 1170.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0170', lv_sum_0170.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0171 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0171 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0171 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0171 TYPE sflight,
        lv_sum_0171 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0171
    WHERE carrid = iv_carrid
      AND seatsocc > 297.
  LOOP AT lt_tmp_0171 INTO ls_tmp_0171.
    lv_sum_0171 = lv_sum_0171 + ls_tmp_0171-seatsocc.
    IF lv_sum_0171 > 1171.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0171', lv_sum_0171.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0172 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0172 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0172 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0172 TYPE sflight,
        lv_sum_0172 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0172
    WHERE carrid = iv_carrid
      AND seatsocc > 4.
  LOOP AT lt_tmp_0172 INTO ls_tmp_0172.
    lv_sum_0172 = lv_sum_0172 + ls_tmp_0172-seatsocc.
    IF lv_sum_0172 > 1172.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0172', lv_sum_0172.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0173 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0173 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0173 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0173 TYPE sflight,
        lv_sum_0173 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0173
    WHERE carrid = iv_carrid
      AND seatsocc > 11.
  LOOP AT lt_tmp_0173 INTO ls_tmp_0173.
    lv_sum_0173 = lv_sum_0173 + ls_tmp_0173-seatsocc.
    IF lv_sum_0173 > 1173.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0173', lv_sum_0173.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0174 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0174 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0174 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0174 TYPE sflight,
        lv_sum_0174 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0174
    WHERE carrid = iv_carrid
      AND seatsocc > 18.
  LOOP AT lt_tmp_0174 INTO ls_tmp_0174.
    lv_sum_0174 = lv_sum_0174 + ls_tmp_0174-seatsocc.
    IF lv_sum_0174 > 1174.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0174', lv_sum_0174.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0175 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0175 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0175 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0175 TYPE sflight,
        lv_sum_0175 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0175
    WHERE carrid = iv_carrid
      AND seatsocc > 25.
  LOOP AT lt_tmp_0175 INTO ls_tmp_0175.
    lv_sum_0175 = lv_sum_0175 + ls_tmp_0175-seatsocc.
    IF lv_sum_0175 > 1175.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0175', lv_sum_0175.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0176 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0176 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0176 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0176 TYPE sflight,
        lv_sum_0176 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0176
    WHERE carrid = iv_carrid
      AND seatsocc > 32.
  LOOP AT lt_tmp_0176 INTO ls_tmp_0176.
    lv_sum_0176 = lv_sum_0176 + ls_tmp_0176-seatsocc.
    IF lv_sum_0176 > 1176.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0176', lv_sum_0176.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0177 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0177 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0177 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0177 TYPE sflight,
        lv_sum_0177 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0177
    WHERE carrid = iv_carrid
      AND seatsocc > 39.
  LOOP AT lt_tmp_0177 INTO ls_tmp_0177.
    lv_sum_0177 = lv_sum_0177 + ls_tmp_0177-seatsocc.
    IF lv_sum_0177 > 1177.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0177', lv_sum_0177.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0178 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0178 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0178 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0178 TYPE sflight,
        lv_sum_0178 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0178
    WHERE carrid = iv_carrid
      AND seatsocc > 46.
  LOOP AT lt_tmp_0178 INTO ls_tmp_0178.
    lv_sum_0178 = lv_sum_0178 + ls_tmp_0178-seatsocc.
    IF lv_sum_0178 > 1178.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0178', lv_sum_0178.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0179 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0179 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0179 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0179 TYPE sflight,
        lv_sum_0179 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0179
    WHERE carrid = iv_carrid
      AND seatsocc > 53.
  LOOP AT lt_tmp_0179 INTO ls_tmp_0179.
    lv_sum_0179 = lv_sum_0179 + ls_tmp_0179-seatsocc.
    IF lv_sum_0179 > 1179.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0179', lv_sum_0179.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0180 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0180 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0180 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0180 TYPE sflight,
        lv_sum_0180 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0180
    WHERE carrid = iv_carrid
      AND seatsocc > 60.
  LOOP AT lt_tmp_0180 INTO ls_tmp_0180.
    lv_sum_0180 = lv_sum_0180 + ls_tmp_0180-seatsocc.
    IF lv_sum_0180 > 1180.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0180', lv_sum_0180.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0181 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0181 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0181 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0181 TYPE sflight,
        lv_sum_0181 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0181
    WHERE carrid = iv_carrid
      AND seatsocc > 67.
  LOOP AT lt_tmp_0181 INTO ls_tmp_0181.
    lv_sum_0181 = lv_sum_0181 + ls_tmp_0181-seatsocc.
    IF lv_sum_0181 > 1181.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0181', lv_sum_0181.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0182 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0182 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0182 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0182 TYPE sflight,
        lv_sum_0182 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0182
    WHERE carrid = iv_carrid
      AND seatsocc > 74.
  LOOP AT lt_tmp_0182 INTO ls_tmp_0182.
    lv_sum_0182 = lv_sum_0182 + ls_tmp_0182-seatsocc.
    IF lv_sum_0182 > 1182.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0182', lv_sum_0182.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0183 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0183 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0183 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0183 TYPE sflight,
        lv_sum_0183 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0183
    WHERE carrid = iv_carrid
      AND seatsocc > 81.
  LOOP AT lt_tmp_0183 INTO ls_tmp_0183.
    lv_sum_0183 = lv_sum_0183 + ls_tmp_0183-seatsocc.
    IF lv_sum_0183 > 1183.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0183', lv_sum_0183.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0184 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0184 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0184 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0184 TYPE sflight,
        lv_sum_0184 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0184
    WHERE carrid = iv_carrid
      AND seatsocc > 88.
  LOOP AT lt_tmp_0184 INTO ls_tmp_0184.
    lv_sum_0184 = lv_sum_0184 + ls_tmp_0184-seatsocc.
    IF lv_sum_0184 > 1184.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0184', lv_sum_0184.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0185 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0185 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0185 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0185 TYPE sflight,
        lv_sum_0185 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0185
    WHERE carrid = iv_carrid
      AND seatsocc > 95.
  LOOP AT lt_tmp_0185 INTO ls_tmp_0185.
    lv_sum_0185 = lv_sum_0185 + ls_tmp_0185-seatsocc.
    IF lv_sum_0185 > 1185.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0185', lv_sum_0185.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0186 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0186 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0186 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0186 TYPE sflight,
        lv_sum_0186 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0186
    WHERE carrid = iv_carrid
      AND seatsocc > 102.
  LOOP AT lt_tmp_0186 INTO ls_tmp_0186.
    lv_sum_0186 = lv_sum_0186 + ls_tmp_0186-seatsocc.
    IF lv_sum_0186 > 1186.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0186', lv_sum_0186.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0187 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0187 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0187 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0187 TYPE sflight,
        lv_sum_0187 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0187
    WHERE carrid = iv_carrid
      AND seatsocc > 109.
  LOOP AT lt_tmp_0187 INTO ls_tmp_0187.
    lv_sum_0187 = lv_sum_0187 + ls_tmp_0187-seatsocc.
    IF lv_sum_0187 > 1187.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0187', lv_sum_0187.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0188 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0188 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0188 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0188 TYPE sflight,
        lv_sum_0188 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0188
    WHERE carrid = iv_carrid
      AND seatsocc > 116.
  LOOP AT lt_tmp_0188 INTO ls_tmp_0188.
    lv_sum_0188 = lv_sum_0188 + ls_tmp_0188-seatsocc.
    IF lv_sum_0188 > 1188.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0188', lv_sum_0188.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0189 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0189 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0189 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0189 TYPE sflight,
        lv_sum_0189 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0189
    WHERE carrid = iv_carrid
      AND seatsocc > 123.
  LOOP AT lt_tmp_0189 INTO ls_tmp_0189.
    lv_sum_0189 = lv_sum_0189 + ls_tmp_0189-seatsocc.
    IF lv_sum_0189 > 1189.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0189', lv_sum_0189.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0190 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0190 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0190 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0190 TYPE sflight,
        lv_sum_0190 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0190
    WHERE carrid = iv_carrid
      AND seatsocc > 130.
  LOOP AT lt_tmp_0190 INTO ls_tmp_0190.
    lv_sum_0190 = lv_sum_0190 + ls_tmp_0190-seatsocc.
    IF lv_sum_0190 > 1190.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0190', lv_sum_0190.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0191 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0191 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0191 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0191 TYPE sflight,
        lv_sum_0191 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0191
    WHERE carrid = iv_carrid
      AND seatsocc > 137.
  LOOP AT lt_tmp_0191 INTO ls_tmp_0191.
    lv_sum_0191 = lv_sum_0191 + ls_tmp_0191-seatsocc.
    IF lv_sum_0191 > 1191.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0191', lv_sum_0191.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0192 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0192 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0192 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0192 TYPE sflight,
        lv_sum_0192 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0192
    WHERE carrid = iv_carrid
      AND seatsocc > 144.
  LOOP AT lt_tmp_0192 INTO ls_tmp_0192.
    lv_sum_0192 = lv_sum_0192 + ls_tmp_0192-seatsocc.
    IF lv_sum_0192 > 1192.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0192', lv_sum_0192.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0193 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0193 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0193 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0193 TYPE sflight,
        lv_sum_0193 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0193
    WHERE carrid = iv_carrid
      AND seatsocc > 151.
  LOOP AT lt_tmp_0193 INTO ls_tmp_0193.
    lv_sum_0193 = lv_sum_0193 + ls_tmp_0193-seatsocc.
    IF lv_sum_0193 > 1193.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0193', lv_sum_0193.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0194 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0194 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0194 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0194 TYPE sflight,
        lv_sum_0194 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0194
    WHERE carrid = iv_carrid
      AND seatsocc > 158.
  LOOP AT lt_tmp_0194 INTO ls_tmp_0194.
    lv_sum_0194 = lv_sum_0194 + ls_tmp_0194-seatsocc.
    IF lv_sum_0194 > 1194.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0194', lv_sum_0194.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0195 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0195 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0195 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0195 TYPE sflight,
        lv_sum_0195 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0195
    WHERE carrid = iv_carrid
      AND seatsocc > 165.
  LOOP AT lt_tmp_0195 INTO ls_tmp_0195.
    lv_sum_0195 = lv_sum_0195 + ls_tmp_0195-seatsocc.
    IF lv_sum_0195 > 1195.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0195', lv_sum_0195.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0196 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0196 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0196 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0196 TYPE sflight,
        lv_sum_0196 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0196
    WHERE carrid = iv_carrid
      AND seatsocc > 172.
  LOOP AT lt_tmp_0196 INTO ls_tmp_0196.
    lv_sum_0196 = lv_sum_0196 + ls_tmp_0196-seatsocc.
    IF lv_sum_0196 > 1196.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0196', lv_sum_0196.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0197 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0197 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0197 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0197 TYPE sflight,
        lv_sum_0197 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0197
    WHERE carrid = iv_carrid
      AND seatsocc > 179.
  LOOP AT lt_tmp_0197 INTO ls_tmp_0197.
    lv_sum_0197 = lv_sum_0197 + ls_tmp_0197-seatsocc.
    IF lv_sum_0197 > 1197.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0197', lv_sum_0197.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0198 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0198 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0198 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0198 TYPE sflight,
        lv_sum_0198 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0198
    WHERE carrid = iv_carrid
      AND seatsocc > 186.
  LOOP AT lt_tmp_0198 INTO ls_tmp_0198.
    lv_sum_0198 = lv_sum_0198 + ls_tmp_0198-seatsocc.
    IF lv_sum_0198 > 1198.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0198', lv_sum_0198.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0199 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0199 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0199 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0199 TYPE sflight,
        lv_sum_0199 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0199
    WHERE carrid = iv_carrid
      AND seatsocc > 193.
  LOOP AT lt_tmp_0199 INTO ls_tmp_0199.
    lv_sum_0199 = lv_sum_0199 + ls_tmp_0199-seatsocc.
    IF lv_sum_0199 > 1199.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0199', lv_sum_0199.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0200 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0200 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0200 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0200 TYPE sflight,
        lv_sum_0200 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0200
    WHERE carrid = iv_carrid
      AND seatsocc > 200.
  LOOP AT lt_tmp_0200 INTO ls_tmp_0200.
    lv_sum_0200 = lv_sum_0200 + ls_tmp_0200-seatsocc.
    IF lv_sum_0200 > 1200.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0200', lv_sum_0200.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0201 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0201 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0201 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0201 TYPE sflight,
        lv_sum_0201 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0201
    WHERE carrid = iv_carrid
      AND seatsocc > 207.
  LOOP AT lt_tmp_0201 INTO ls_tmp_0201.
    lv_sum_0201 = lv_sum_0201 + ls_tmp_0201-seatsocc.
    IF lv_sum_0201 > 1201.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0201', lv_sum_0201.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0202 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0202 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0202 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0202 TYPE sflight,
        lv_sum_0202 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0202
    WHERE carrid = iv_carrid
      AND seatsocc > 214.
  LOOP AT lt_tmp_0202 INTO ls_tmp_0202.
    lv_sum_0202 = lv_sum_0202 + ls_tmp_0202-seatsocc.
    IF lv_sum_0202 > 1202.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0202', lv_sum_0202.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0203 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0203 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0203 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0203 TYPE sflight,
        lv_sum_0203 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0203
    WHERE carrid = iv_carrid
      AND seatsocc > 221.
  LOOP AT lt_tmp_0203 INTO ls_tmp_0203.
    lv_sum_0203 = lv_sum_0203 + ls_tmp_0203-seatsocc.
    IF lv_sum_0203 > 1203.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0203', lv_sum_0203.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0204 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0204 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0204 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0204 TYPE sflight,
        lv_sum_0204 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0204
    WHERE carrid = iv_carrid
      AND seatsocc > 228.
  LOOP AT lt_tmp_0204 INTO ls_tmp_0204.
    lv_sum_0204 = lv_sum_0204 + ls_tmp_0204-seatsocc.
    IF lv_sum_0204 > 1204.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0204', lv_sum_0204.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0205 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0205 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0205 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0205 TYPE sflight,
        lv_sum_0205 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0205
    WHERE carrid = iv_carrid
      AND seatsocc > 235.
  LOOP AT lt_tmp_0205 INTO ls_tmp_0205.
    lv_sum_0205 = lv_sum_0205 + ls_tmp_0205-seatsocc.
    IF lv_sum_0205 > 1205.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0205', lv_sum_0205.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0206 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0206 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0206 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0206 TYPE sflight,
        lv_sum_0206 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0206
    WHERE carrid = iv_carrid
      AND seatsocc > 242.
  LOOP AT lt_tmp_0206 INTO ls_tmp_0206.
    lv_sum_0206 = lv_sum_0206 + ls_tmp_0206-seatsocc.
    IF lv_sum_0206 > 1206.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0206', lv_sum_0206.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0207 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0207 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0207 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0207 TYPE sflight,
        lv_sum_0207 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0207
    WHERE carrid = iv_carrid
      AND seatsocc > 249.
  LOOP AT lt_tmp_0207 INTO ls_tmp_0207.
    lv_sum_0207 = lv_sum_0207 + ls_tmp_0207-seatsocc.
    IF lv_sum_0207 > 1207.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0207', lv_sum_0207.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0208 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0208 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0208 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0208 TYPE sflight,
        lv_sum_0208 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0208
    WHERE carrid = iv_carrid
      AND seatsocc > 256.
  LOOP AT lt_tmp_0208 INTO ls_tmp_0208.
    lv_sum_0208 = lv_sum_0208 + ls_tmp_0208-seatsocc.
    IF lv_sum_0208 > 1208.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0208', lv_sum_0208.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0209 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0209 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0209 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0209 TYPE sflight,
        lv_sum_0209 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0209
    WHERE carrid = iv_carrid
      AND seatsocc > 263.
  LOOP AT lt_tmp_0209 INTO ls_tmp_0209.
    lv_sum_0209 = lv_sum_0209 + ls_tmp_0209-seatsocc.
    IF lv_sum_0209 > 1209.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0209', lv_sum_0209.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0210 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0210 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0210 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0210 TYPE sflight,
        lv_sum_0210 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0210
    WHERE carrid = iv_carrid
      AND seatsocc > 270.
  LOOP AT lt_tmp_0210 INTO ls_tmp_0210.
    lv_sum_0210 = lv_sum_0210 + ls_tmp_0210-seatsocc.
    IF lv_sum_0210 > 1210.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0210', lv_sum_0210.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0211 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0211 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0211 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0211 TYPE sflight,
        lv_sum_0211 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0211
    WHERE carrid = iv_carrid
      AND seatsocc > 277.
  LOOP AT lt_tmp_0211 INTO ls_tmp_0211.
    lv_sum_0211 = lv_sum_0211 + ls_tmp_0211-seatsocc.
    IF lv_sum_0211 > 1211.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0211', lv_sum_0211.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0212 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0212 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0212 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0212 TYPE sflight,
        lv_sum_0212 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0212
    WHERE carrid = iv_carrid
      AND seatsocc > 284.
  LOOP AT lt_tmp_0212 INTO ls_tmp_0212.
    lv_sum_0212 = lv_sum_0212 + ls_tmp_0212-seatsocc.
    IF lv_sum_0212 > 1212.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0212', lv_sum_0212.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0213 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0213 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0213 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0213 TYPE sflight,
        lv_sum_0213 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0213
    WHERE carrid = iv_carrid
      AND seatsocc > 291.
  LOOP AT lt_tmp_0213 INTO ls_tmp_0213.
    lv_sum_0213 = lv_sum_0213 + ls_tmp_0213-seatsocc.
    IF lv_sum_0213 > 1213.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0213', lv_sum_0213.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0214 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0214 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0214 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0214 TYPE sflight,
        lv_sum_0214 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0214
    WHERE carrid = iv_carrid
      AND seatsocc > 298.
  LOOP AT lt_tmp_0214 INTO ls_tmp_0214.
    lv_sum_0214 = lv_sum_0214 + ls_tmp_0214-seatsocc.
    IF lv_sum_0214 > 1214.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0214', lv_sum_0214.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0215 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0215 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0215 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0215 TYPE sflight,
        lv_sum_0215 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0215
    WHERE carrid = iv_carrid
      AND seatsocc > 5.
  LOOP AT lt_tmp_0215 INTO ls_tmp_0215.
    lv_sum_0215 = lv_sum_0215 + ls_tmp_0215-seatsocc.
    IF lv_sum_0215 > 1215.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0215', lv_sum_0215.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0216 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0216 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0216 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0216 TYPE sflight,
        lv_sum_0216 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0216
    WHERE carrid = iv_carrid
      AND seatsocc > 12.
  LOOP AT lt_tmp_0216 INTO ls_tmp_0216.
    lv_sum_0216 = lv_sum_0216 + ls_tmp_0216-seatsocc.
    IF lv_sum_0216 > 1216.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0216', lv_sum_0216.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0217 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0217 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0217 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0217 TYPE sflight,
        lv_sum_0217 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0217
    WHERE carrid = iv_carrid
      AND seatsocc > 19.
  LOOP AT lt_tmp_0217 INTO ls_tmp_0217.
    lv_sum_0217 = lv_sum_0217 + ls_tmp_0217-seatsocc.
    IF lv_sum_0217 > 1217.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0217', lv_sum_0217.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0218 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0218 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0218 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0218 TYPE sflight,
        lv_sum_0218 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0218
    WHERE carrid = iv_carrid
      AND seatsocc > 26.
  LOOP AT lt_tmp_0218 INTO ls_tmp_0218.
    lv_sum_0218 = lv_sum_0218 + ls_tmp_0218-seatsocc.
    IF lv_sum_0218 > 1218.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0218', lv_sum_0218.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0219 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0219 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0219 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0219 TYPE sflight,
        lv_sum_0219 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0219
    WHERE carrid = iv_carrid
      AND seatsocc > 33.
  LOOP AT lt_tmp_0219 INTO ls_tmp_0219.
    lv_sum_0219 = lv_sum_0219 + ls_tmp_0219-seatsocc.
    IF lv_sum_0219 > 1219.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0219', lv_sum_0219.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0220 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0220 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0220 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0220 TYPE sflight,
        lv_sum_0220 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0220
    WHERE carrid = iv_carrid
      AND seatsocc > 40.
  LOOP AT lt_tmp_0220 INTO ls_tmp_0220.
    lv_sum_0220 = lv_sum_0220 + ls_tmp_0220-seatsocc.
    IF lv_sum_0220 > 1220.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0220', lv_sum_0220.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0221 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0221 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0221 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0221 TYPE sflight,
        lv_sum_0221 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0221
    WHERE carrid = iv_carrid
      AND seatsocc > 47.
  LOOP AT lt_tmp_0221 INTO ls_tmp_0221.
    lv_sum_0221 = lv_sum_0221 + ls_tmp_0221-seatsocc.
    IF lv_sum_0221 > 1221.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0221', lv_sum_0221.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0222 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0222 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0222 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0222 TYPE sflight,
        lv_sum_0222 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0222
    WHERE carrid = iv_carrid
      AND seatsocc > 54.
  LOOP AT lt_tmp_0222 INTO ls_tmp_0222.
    lv_sum_0222 = lv_sum_0222 + ls_tmp_0222-seatsocc.
    IF lv_sum_0222 > 1222.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0222', lv_sum_0222.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0223 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0223 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0223 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0223 TYPE sflight,
        lv_sum_0223 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0223
    WHERE carrid = iv_carrid
      AND seatsocc > 61.
  LOOP AT lt_tmp_0223 INTO ls_tmp_0223.
    lv_sum_0223 = lv_sum_0223 + ls_tmp_0223-seatsocc.
    IF lv_sum_0223 > 1223.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0223', lv_sum_0223.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0224 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0224 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0224 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0224 TYPE sflight,
        lv_sum_0224 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0224
    WHERE carrid = iv_carrid
      AND seatsocc > 68.
  LOOP AT lt_tmp_0224 INTO ls_tmp_0224.
    lv_sum_0224 = lv_sum_0224 + ls_tmp_0224-seatsocc.
    IF lv_sum_0224 > 1224.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0224', lv_sum_0224.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0225 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0225 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0225 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0225 TYPE sflight,
        lv_sum_0225 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0225
    WHERE carrid = iv_carrid
      AND seatsocc > 75.
  LOOP AT lt_tmp_0225 INTO ls_tmp_0225.
    lv_sum_0225 = lv_sum_0225 + ls_tmp_0225-seatsocc.
    IF lv_sum_0225 > 1225.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0225', lv_sum_0225.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0226 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0226 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0226 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0226 TYPE sflight,
        lv_sum_0226 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0226
    WHERE carrid = iv_carrid
      AND seatsocc > 82.
  LOOP AT lt_tmp_0226 INTO ls_tmp_0226.
    lv_sum_0226 = lv_sum_0226 + ls_tmp_0226-seatsocc.
    IF lv_sum_0226 > 1226.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0226', lv_sum_0226.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0227 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0227 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0227 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0227 TYPE sflight,
        lv_sum_0227 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0227
    WHERE carrid = iv_carrid
      AND seatsocc > 89.
  LOOP AT lt_tmp_0227 INTO ls_tmp_0227.
    lv_sum_0227 = lv_sum_0227 + ls_tmp_0227-seatsocc.
    IF lv_sum_0227 > 1227.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0227', lv_sum_0227.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0228 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0228 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0228 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0228 TYPE sflight,
        lv_sum_0228 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0228
    WHERE carrid = iv_carrid
      AND seatsocc > 96.
  LOOP AT lt_tmp_0228 INTO ls_tmp_0228.
    lv_sum_0228 = lv_sum_0228 + ls_tmp_0228-seatsocc.
    IF lv_sum_0228 > 1228.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0228', lv_sum_0228.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0229 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0229 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0229 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0229 TYPE sflight,
        lv_sum_0229 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0229
    WHERE carrid = iv_carrid
      AND seatsocc > 103.
  LOOP AT lt_tmp_0229 INTO ls_tmp_0229.
    lv_sum_0229 = lv_sum_0229 + ls_tmp_0229-seatsocc.
    IF lv_sum_0229 > 1229.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0229', lv_sum_0229.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0230 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0230 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0230 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0230 TYPE sflight,
        lv_sum_0230 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0230
    WHERE carrid = iv_carrid
      AND seatsocc > 110.
  LOOP AT lt_tmp_0230 INTO ls_tmp_0230.
    lv_sum_0230 = lv_sum_0230 + ls_tmp_0230-seatsocc.
    IF lv_sum_0230 > 1230.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0230', lv_sum_0230.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0231 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0231 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0231 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0231 TYPE sflight,
        lv_sum_0231 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0231
    WHERE carrid = iv_carrid
      AND seatsocc > 117.
  LOOP AT lt_tmp_0231 INTO ls_tmp_0231.
    lv_sum_0231 = lv_sum_0231 + ls_tmp_0231-seatsocc.
    IF lv_sum_0231 > 1231.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0231', lv_sum_0231.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0232 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0232 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0232 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0232 TYPE sflight,
        lv_sum_0232 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0232
    WHERE carrid = iv_carrid
      AND seatsocc > 124.
  LOOP AT lt_tmp_0232 INTO ls_tmp_0232.
    lv_sum_0232 = lv_sum_0232 + ls_tmp_0232-seatsocc.
    IF lv_sum_0232 > 1232.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0232', lv_sum_0232.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0233 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0233 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0233 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0233 TYPE sflight,
        lv_sum_0233 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0233
    WHERE carrid = iv_carrid
      AND seatsocc > 131.
  LOOP AT lt_tmp_0233 INTO ls_tmp_0233.
    lv_sum_0233 = lv_sum_0233 + ls_tmp_0233-seatsocc.
    IF lv_sum_0233 > 1233.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0233', lv_sum_0233.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0234 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0234 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0234 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0234 TYPE sflight,
        lv_sum_0234 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0234
    WHERE carrid = iv_carrid
      AND seatsocc > 138.
  LOOP AT lt_tmp_0234 INTO ls_tmp_0234.
    lv_sum_0234 = lv_sum_0234 + ls_tmp_0234-seatsocc.
    IF lv_sum_0234 > 1234.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0234', lv_sum_0234.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0235 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0235 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0235 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0235 TYPE sflight,
        lv_sum_0235 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0235
    WHERE carrid = iv_carrid
      AND seatsocc > 145.
  LOOP AT lt_tmp_0235 INTO ls_tmp_0235.
    lv_sum_0235 = lv_sum_0235 + ls_tmp_0235-seatsocc.
    IF lv_sum_0235 > 1235.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0235', lv_sum_0235.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0236 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0236 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0236 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0236 TYPE sflight,
        lv_sum_0236 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0236
    WHERE carrid = iv_carrid
      AND seatsocc > 152.
  LOOP AT lt_tmp_0236 INTO ls_tmp_0236.
    lv_sum_0236 = lv_sum_0236 + ls_tmp_0236-seatsocc.
    IF lv_sum_0236 > 1236.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0236', lv_sum_0236.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0237 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0237 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0237 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0237 TYPE sflight,
        lv_sum_0237 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0237
    WHERE carrid = iv_carrid
      AND seatsocc > 159.
  LOOP AT lt_tmp_0237 INTO ls_tmp_0237.
    lv_sum_0237 = lv_sum_0237 + ls_tmp_0237-seatsocc.
    IF lv_sum_0237 > 1237.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0237', lv_sum_0237.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0238 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0238 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0238 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0238 TYPE sflight,
        lv_sum_0238 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0238
    WHERE carrid = iv_carrid
      AND seatsocc > 166.
  LOOP AT lt_tmp_0238 INTO ls_tmp_0238.
    lv_sum_0238 = lv_sum_0238 + ls_tmp_0238-seatsocc.
    IF lv_sum_0238 > 1238.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0238', lv_sum_0238.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0239 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0239 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0239 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0239 TYPE sflight,
        lv_sum_0239 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0239
    WHERE carrid = iv_carrid
      AND seatsocc > 173.
  LOOP AT lt_tmp_0239 INTO ls_tmp_0239.
    lv_sum_0239 = lv_sum_0239 + ls_tmp_0239-seatsocc.
    IF lv_sum_0239 > 1239.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0239', lv_sum_0239.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0240 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0240 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0240 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0240 TYPE sflight,
        lv_sum_0240 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0240
    WHERE carrid = iv_carrid
      AND seatsocc > 180.
  LOOP AT lt_tmp_0240 INTO ls_tmp_0240.
    lv_sum_0240 = lv_sum_0240 + ls_tmp_0240-seatsocc.
    IF lv_sum_0240 > 1240.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0240', lv_sum_0240.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0241 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0241 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0241 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0241 TYPE sflight,
        lv_sum_0241 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0241
    WHERE carrid = iv_carrid
      AND seatsocc > 187.
  LOOP AT lt_tmp_0241 INTO ls_tmp_0241.
    lv_sum_0241 = lv_sum_0241 + ls_tmp_0241-seatsocc.
    IF lv_sum_0241 > 1241.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0241', lv_sum_0241.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0242 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0242 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0242 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0242 TYPE sflight,
        lv_sum_0242 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0242
    WHERE carrid = iv_carrid
      AND seatsocc > 194.
  LOOP AT lt_tmp_0242 INTO ls_tmp_0242.
    lv_sum_0242 = lv_sum_0242 + ls_tmp_0242-seatsocc.
    IF lv_sum_0242 > 1242.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0242', lv_sum_0242.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0243 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0243 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0243 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0243 TYPE sflight,
        lv_sum_0243 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0243
    WHERE carrid = iv_carrid
      AND seatsocc > 201.
  LOOP AT lt_tmp_0243 INTO ls_tmp_0243.
    lv_sum_0243 = lv_sum_0243 + ls_tmp_0243-seatsocc.
    IF lv_sum_0243 > 1243.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0243', lv_sum_0243.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0244 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0244 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0244 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0244 TYPE sflight,
        lv_sum_0244 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0244
    WHERE carrid = iv_carrid
      AND seatsocc > 208.
  LOOP AT lt_tmp_0244 INTO ls_tmp_0244.
    lv_sum_0244 = lv_sum_0244 + ls_tmp_0244-seatsocc.
    IF lv_sum_0244 > 1244.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0244', lv_sum_0244.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0245 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0245 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0245 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0245 TYPE sflight,
        lv_sum_0245 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0245
    WHERE carrid = iv_carrid
      AND seatsocc > 215.
  LOOP AT lt_tmp_0245 INTO ls_tmp_0245.
    lv_sum_0245 = lv_sum_0245 + ls_tmp_0245-seatsocc.
    IF lv_sum_0245 > 1245.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0245', lv_sum_0245.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0246 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0246 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0246 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0246 TYPE sflight,
        lv_sum_0246 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0246
    WHERE carrid = iv_carrid
      AND seatsocc > 222.
  LOOP AT lt_tmp_0246 INTO ls_tmp_0246.
    lv_sum_0246 = lv_sum_0246 + ls_tmp_0246-seatsocc.
    IF lv_sum_0246 > 1246.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0246', lv_sum_0246.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0247 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0247 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0247 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0247 TYPE sflight,
        lv_sum_0247 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0247
    WHERE carrid = iv_carrid
      AND seatsocc > 229.
  LOOP AT lt_tmp_0247 INTO ls_tmp_0247.
    lv_sum_0247 = lv_sum_0247 + ls_tmp_0247-seatsocc.
    IF lv_sum_0247 > 1247.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0247', lv_sum_0247.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0248 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0248 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0248 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0248 TYPE sflight,
        lv_sum_0248 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0248
    WHERE carrid = iv_carrid
      AND seatsocc > 236.
  LOOP AT lt_tmp_0248 INTO ls_tmp_0248.
    lv_sum_0248 = lv_sum_0248 + ls_tmp_0248-seatsocc.
    IF lv_sum_0248 > 1248.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0248', lv_sum_0248.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0249 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0249 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0249 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0249 TYPE sflight,
        lv_sum_0249 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0249
    WHERE carrid = iv_carrid
      AND seatsocc > 243.
  LOOP AT lt_tmp_0249 INTO ls_tmp_0249.
    lv_sum_0249 = lv_sum_0249 + ls_tmp_0249-seatsocc.
    IF lv_sum_0249 > 1249.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0249', lv_sum_0249.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0250 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0250 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0250 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0250 TYPE sflight,
        lv_sum_0250 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0250
    WHERE carrid = iv_carrid
      AND seatsocc > 250.
  LOOP AT lt_tmp_0250 INTO ls_tmp_0250.
    lv_sum_0250 = lv_sum_0250 + ls_tmp_0250-seatsocc.
    IF lv_sum_0250 > 1250.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0250', lv_sum_0250.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0251 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0251 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0251 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0251 TYPE sflight,
        lv_sum_0251 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0251
    WHERE carrid = iv_carrid
      AND seatsocc > 257.
  LOOP AT lt_tmp_0251 INTO ls_tmp_0251.
    lv_sum_0251 = lv_sum_0251 + ls_tmp_0251-seatsocc.
    IF lv_sum_0251 > 1251.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0251', lv_sum_0251.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0252 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0252 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0252 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0252 TYPE sflight,
        lv_sum_0252 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0252
    WHERE carrid = iv_carrid
      AND seatsocc > 264.
  LOOP AT lt_tmp_0252 INTO ls_tmp_0252.
    lv_sum_0252 = lv_sum_0252 + ls_tmp_0252-seatsocc.
    IF lv_sum_0252 > 1252.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0252', lv_sum_0252.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0253 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0253 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0253 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0253 TYPE sflight,
        lv_sum_0253 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0253
    WHERE carrid = iv_carrid
      AND seatsocc > 271.
  LOOP AT lt_tmp_0253 INTO ls_tmp_0253.
    lv_sum_0253 = lv_sum_0253 + ls_tmp_0253-seatsocc.
    IF lv_sum_0253 > 1253.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0253', lv_sum_0253.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0254 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0254 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0254 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0254 TYPE sflight,
        lv_sum_0254 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0254
    WHERE carrid = iv_carrid
      AND seatsocc > 278.
  LOOP AT lt_tmp_0254 INTO ls_tmp_0254.
    lv_sum_0254 = lv_sum_0254 + ls_tmp_0254-seatsocc.
    IF lv_sum_0254 > 1254.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0254', lv_sum_0254.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0255 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0255 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0255 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0255 TYPE sflight,
        lv_sum_0255 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0255
    WHERE carrid = iv_carrid
      AND seatsocc > 285.
  LOOP AT lt_tmp_0255 INTO ls_tmp_0255.
    lv_sum_0255 = lv_sum_0255 + ls_tmp_0255-seatsocc.
    IF lv_sum_0255 > 1255.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0255', lv_sum_0255.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0256 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0256 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0256 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0256 TYPE sflight,
        lv_sum_0256 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0256
    WHERE carrid = iv_carrid
      AND seatsocc > 292.
  LOOP AT lt_tmp_0256 INTO ls_tmp_0256.
    lv_sum_0256 = lv_sum_0256 + ls_tmp_0256-seatsocc.
    IF lv_sum_0256 > 1256.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0256', lv_sum_0256.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0257 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0257 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0257 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0257 TYPE sflight,
        lv_sum_0257 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0257
    WHERE carrid = iv_carrid
      AND seatsocc > 299.
  LOOP AT lt_tmp_0257 INTO ls_tmp_0257.
    lv_sum_0257 = lv_sum_0257 + ls_tmp_0257-seatsocc.
    IF lv_sum_0257 > 1257.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0257', lv_sum_0257.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0258 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0258 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0258 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0258 TYPE sflight,
        lv_sum_0258 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0258
    WHERE carrid = iv_carrid
      AND seatsocc > 6.
  LOOP AT lt_tmp_0258 INTO ls_tmp_0258.
    lv_sum_0258 = lv_sum_0258 + ls_tmp_0258-seatsocc.
    IF lv_sum_0258 > 1258.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0258', lv_sum_0258.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0259 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0259 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0259 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0259 TYPE sflight,
        lv_sum_0259 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0259
    WHERE carrid = iv_carrid
      AND seatsocc > 13.
  LOOP AT lt_tmp_0259 INTO ls_tmp_0259.
    lv_sum_0259 = lv_sum_0259 + ls_tmp_0259-seatsocc.
    IF lv_sum_0259 > 1259.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0259', lv_sum_0259.
ENDFORM.

*&---------------------------------------------------------------------*
*& Form OLD_ROUTINE_0260 - obsolete, kept for reference (not called)
*&---------------------------------------------------------------------*
FORM old_routine_0260 USING iv_carrid TYPE sflight-carrid.
  DATA: lt_tmp_0260 TYPE STANDARD TABLE OF sflight,
        ls_tmp_0260 TYPE sflight,
        lv_sum_0260 TYPE i.
  SELECT * FROM sflight INTO TABLE lt_tmp_0260
    WHERE carrid = iv_carrid
      AND seatsocc > 20.
  LOOP AT lt_tmp_0260 INTO ls_tmp_0260.
    lv_sum_0260 = lv_sum_0260 + ls_tmp_0260-seatsocc.
    IF lv_sum_0260 > 1260.
      EXIT.
    ENDIF.
  ENDLOOP.
  WRITE: / 'Routine 0260', lv_sum_0260.
ENDFORM.
