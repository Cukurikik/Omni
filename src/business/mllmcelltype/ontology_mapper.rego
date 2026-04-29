package mllmcelltype.ontology

default valid_mapping = false

valid_mapping {
    input.cell_type != ""
    input.confidence_score >= 0.85
    input.database_version == "CellOntology_v2"
}

omni_result = {
    "value": valid_mapping,
    "error": null,
    "is_ok": true
}
