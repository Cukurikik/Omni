"OMNI Debugging & Inspection Layer"
"Smalltalk/Pharo live object inspection mapping to native Omni memory spaces."

Object subclass: #OmniLiveInspector
    instanceVariableNames: 'memoryAddress bufferSize nativeHandle'
    classVariableNames: ''
    package: 'Omni-Debugger'

OmniLiveInspector >> initializeWithAddress: anAddress size: anInteger [
    memoryAddress := anAddress.
    bufferSize := anInteger.
    nativeHandle := ExternalAddress fromAddress: anAddress.
]

OmniLiveInspector >> readFloatAt: index [
    "Reads a 32-bit float from the native Omni memory space (0-indexed)"
    | offset floatValue |
    (index < 0 or: [index >= bufferSize]) ifTrue: [
        ^ Error signal: 'Omni Memory bounds exceeded'.
    ].
    offset := index * 4.
    floatValue := nativeHandle floatAt: offset + 1. "Pharo is 1-indexed"
    ^ floatValue
]

OmniLiveInspector >> visualizeTensorData [
    "Opens a live Roassal plot of the transformer attention weights"
    | weights b |
    weights := OrderedCollection new.
    0 to: (bufferSize min: 100) - 1 do: [ :i |
        weights add: (self readFloatAt: i)
    ].
    
    b := Rsviz new.
    b title: 'Omni Attention Live Weights'.
    b addPlot: (RsLinePlot new y: weights).
    b open.
]

OmniLiveInspector class >> attachToOmniProcess: pid [
    "Simulates attaching to the OS-level Omni Universal Binary process"
    | inspector addr |
    addr := 16r7FF00000. "Mocked base address of shared memory segment"
    inspector := self new initializeWithAddress: addr size: 4096.
    ^ inspector
]
