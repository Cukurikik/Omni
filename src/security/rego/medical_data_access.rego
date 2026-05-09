package omni.medical.data

default allow = false

allow {
    input.user_clearance == "HIPAA_COMPLIANT"
    input.action == "read_dicom"
}
