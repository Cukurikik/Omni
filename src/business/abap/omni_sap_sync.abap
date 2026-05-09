*&---------------------------------------------------------------------*
*& Report ZOMNI_SYNC_ERP
*&---------------------------------------------------------------------*
*& OMNI Framework - SAP ABAP Sync Module
*& Pushes inventory and financial data from SAP to OMNI Nexus
*&---------------------------------------------------------------------*
REPORT ZOMNI_SYNC_ERP.

DATA: lo_http_client TYPE REF TO if_http_client,
      lv_url         TYPE string VALUE 'https://nexus.omniframework.dev/api/v1/erp/sync',
      lv_body        TYPE string,
      lv_json        TYPE string.

* Construct payload
lv_json = '{"plant": "1000", "material": "OMNI-CORE-01", "stock": 500}'.

* Create HTTP Client
CALL METHOD cl_http_client=>create_by_url
  EXPORTING
    url                = lv_url
  IMPORTING
    client             = lo_http_client
  EXCEPTIONS
    argument_not_found = 1
    plugin_not_active  = 2
    internal_error     = 3
    OTHERS             = 4.

IF sy-subrc = 0.
  lo_http_client->request->set_method( 'POST' ).
  lo_http_client->request->set_content_type( 'application/json' ).
  lo_http_client->request->set_cdata( lv_json ).

  CALL METHOD lo_http_client->send
    EXCEPTIONS
      http_communication_failure = 1
      http_invalid_state         = 2
      http_processing_failed     = 3
      OTHERS                     = 4.

  IF sy-subrc = 0.
    CALL METHOD lo_http_client->receive
      EXCEPTIONS
        http_communication_failure = 1
        http_invalid_state         = 2
        http_processing_failed     = 3
        OTHERS                     = 4.
        
    IF sy-subrc = 0.
      WRITE: / 'Sync to OMNI successful.'.
    ELSE.
      WRITE: / 'Failed to receive response from OMNI.'.
    ENDIF.
  ELSE.
    WRITE: / 'Failed to send request to OMNI.'.
  ENDIF.
  
  lo_http_client->close( ).
ENDIF.
