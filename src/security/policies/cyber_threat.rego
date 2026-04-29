package omni.cyber

default block_ip = false

block_ip {
    input.request.failed_logins > 5
}
block_ip {
    input.request.threat_score > 0.8
}
