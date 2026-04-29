package sftdatasets.license

default is_license_allowed = false

allowed_licenses = {"MIT", "Apache-2.0", "CC-BY-4.0"}

is_license_allowed {
    allowed_licenses[input.license_type]
}

omni_result = {
    "value": is_license_allowed,
    "error": null,
    "is_ok": true
}
