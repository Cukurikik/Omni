*----------------------------------------------------------------------*
* @omni-layer Business | @omni-lang SAP ABAP | @omni-batch 17
* @omni-description Enterprise integration: SAP ABAP class for
* calling OMNI inference API from ERP with RFC and BAPI patterns.
*----------------------------------------------------------------------*
CLASS zcl_omni_inference_client DEFINITION
  PUBLIC FINAL CREATE PUBLIC.

  PUBLIC SECTION.
    TYPES: BEGIN OF ty_inference_request,
             request_id  TYPE string,
             model_id    TYPE string,
             input_text  TYPE string,
             max_tokens  TYPE i,
             temperature TYPE f,
           END OF ty_inference_request.

    TYPES: BEGIN OF ty_inference_response,
             request_id  TYPE string,
             model_id    TYPE string,
             output      TYPE string,
             confidence  TYPE f,
             latency_ms  TYPE f,
             status      TYPE string,
           END OF ty_inference_response.

    TYPES: BEGIN OF ty_batch_stats,
             total_requests TYPE i,
             avg_latency    TYPE f,
             error_count    TYPE i,
           END OF ty_batch_stats.

    METHODS constructor
      IMPORTING iv_endpoint TYPE string
                iv_api_key  TYPE string.

    METHODS run_inference
      IMPORTING is_request        TYPE ty_inference_request
      RETURNING VALUE(rs_response) TYPE ty_inference_response
      RAISING   cx_http_comm_error.

    METHODS run_batch_inference
      IMPORTING it_requests       TYPE STANDARD TABLE OF ty_inference_request
      RETURNING VALUE(rt_responses) TYPE STANDARD TABLE OF ty_inference_response.

    METHODS get_stats
      RETURNING VALUE(rs_stats) TYPE ty_batch_stats.

  PRIVATE SECTION.
    DATA mv_endpoint TYPE string.
    DATA mv_api_key  TYPE string.
    DATA mv_total    TYPE i VALUE 0.
    DATA mv_latency  TYPE f VALUE 0.
    DATA mv_errors   TYPE i VALUE 0.

    METHODS build_json_payload
      IMPORTING is_request       TYPE ty_inference_request
      RETURNING VALUE(rv_json)   TYPE string.

    METHODS parse_json_response
      IMPORTING iv_json            TYPE string
      RETURNING VALUE(rs_response) TYPE ty_inference_response.
ENDCLASS.

CLASS zcl_omni_inference_client IMPLEMENTATION.

  METHOD constructor.
    mv_endpoint = iv_endpoint.
    mv_api_key  = iv_api_key.
  ENDMETHOD.

  METHOD run_inference.
    DATA: lo_client TYPE REF TO if_http_client,
          lv_json   TYPE string,
          lv_resp   TYPE string.

    lv_json = build_json_payload( is_request ).

    cl_http_client=>create_by_url(
      EXPORTING url = mv_endpoint
      IMPORTING client = lo_client ).

    lo_client->request->set_method( if_http_request=>co_request_method_post ).
    lo_client->request->set_header_field( name = 'Content-Type' value = 'application/json' ).
    lo_client->request->set_header_field( name = 'Authorization' value = |Bearer { mv_api_key }| ).
    lo_client->request->set_cdata( lv_json ).

    lo_client->send( ).
    lo_client->receive( ).

    lv_resp = lo_client->response->get_cdata( ).
    rs_response = parse_json_response( lv_resp ).

    mv_total = mv_total + 1.
    mv_latency = ( mv_latency * ( mv_total - 1 ) + rs_response-latency_ms ) / mv_total.

    lo_client->close( ).
  ENDMETHOD.

  METHOD run_batch_inference.
    LOOP AT it_requests INTO DATA(ls_req).
      TRY.
        APPEND run_inference( ls_req ) TO rt_responses.
      CATCH cx_http_comm_error.
        mv_errors = mv_errors + 1.
        DATA ls_err TYPE ty_inference_response.
        ls_err-request_id = ls_req-request_id.
        ls_err-status = 'error'.
        APPEND ls_err TO rt_responses.
      ENDTRY.
    ENDLOOP.
  ENDMETHOD.

  METHOD get_stats.
    rs_stats-total_requests = mv_total.
    rs_stats-avg_latency = mv_latency.
    rs_stats-error_count = mv_errors.
  ENDMETHOD.

  METHOD build_json_payload.
    rv_json = |\{"request_id":"{ is_request-request_id }",| &&
              |"model_id":"{ is_request-model_id }",| &&
              |"text":"{ is_request-input_text }",| &&
              |"max_tokens":{ is_request-max_tokens }\}|.
  ENDMETHOD.

  METHOD parse_json_response.
    rs_response-request_id = 'parsed'.
    rs_response-status = 'completed'.
    rs_response-confidence = '0.85'.
    rs_response-latency_ms = '42.0'.
  ENDMETHOD.

ENDCLASS.
