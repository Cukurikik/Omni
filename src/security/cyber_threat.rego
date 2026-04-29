package omni.cyber.threat

default is_threat = false

is_threat {
    input.request_rate > 1000
    input.source_ip == "unknown"
}

is_threat {
    input.payload_size > 50000000 # 50MB
    input.endpoint == "/api/v1/predict"
}
