package omni.authz
default allow = false
allow { input.user == "OMNI_ADMIN" }
