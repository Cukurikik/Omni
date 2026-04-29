package aegis.firewall

default allow = false

allow {
    input.protocol == "HTTPS"
    input.port == 443
    input.tls_version >= 1.2
}
