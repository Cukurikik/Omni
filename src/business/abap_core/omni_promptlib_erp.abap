* Omni Promptlib ERP (ABAP)
* Business Layer: Core enterprise prompt ingestion and validation for SAP systems.

CLASS zcl_omni_promptlib DEFINITION PUBLIC FINAL.
  PUBLIC SECTION.
    TYPES: BEGIN OF t_prompt_result,
             success TYPE abap_bool,
             content TYPE string,
             error   TYPE string,
           END OF t_prompt_result.

    CLASS-METHODS: sanitize_prompt
      IMPORTING iv_prompt TYPE string
      RETURNING VALUE(rv_result) TYPE t_prompt_result.
ENDCLASS.

CLASS zcl_omni_promptlib IMPLEMENTATION.
  METHOD sanitize_prompt.
    IF iv_prompt IS INITIAL.
      rv_result-success = abap_false.
      rv_result-error   = 'Prompt cannot be empty'.
      RETURN.
    ENDIF.

    " Deterministic validation
    FIND SUBSTRING '<script>' IN iv_prompt.
    IF sy-subrc = 0.
      rv_result-success = abap_false.
      rv_result-error   = 'Forbidden injection vector detected'.
      RETURN.
    ENDIF.

    rv_result-success = abap_true.
    rv_result-content = iv_prompt.
  ENDMETHOD.
ENDCLASS.
