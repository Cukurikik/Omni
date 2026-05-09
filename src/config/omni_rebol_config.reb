Rebol [
    Title: "OMNI Node Configuration"
    Date: 3-May-2026
    Version: 3.1.4
    Purpose: "Human-readable data exchange format for bootstrapping the Omni Native Engine"
]

; OMNI Configuration Layer
; Rebol's dialecting capabilities make it ideal for defining complex execution parameters
; without the syntactic noise of JSON or XML.

omni-system-config: [
    node-id: "omni-edge-alpha-7"
    environment: production
    
    network: [
        rpc-port: 50051
        ws-port: 8081
        allowed-peers: [10.0.1.101 10.0.1.102 10.0.1.103]
    ]
    
    execution-engine: [
        binary-path: %/opt/omni/bin/omni_universal_binary.so
        threading-model: adaptive
        max-threads: 32
        
        hardware-targets: [
            avx512: true
            cuda: false
            metal: false
        ]
    ]
    
    models: [
        [
            id: "gpt-neo-omni"
            precision: int8
            memory-pinning: true
            path: %/mnt/models/gpt-neo.omnimodel
        ]
        [
            id: "omni-vision-transformer"
            precision: fp16
            memory-pinning: true
            path: %/mnt/models/vit.omnimodel
        ]
    ]
]

print "OMNI Rebol Configuration Loaded."
print ["Bootstrapping Node:" select omni-system-config 'node-id]
