"Omni Domain Object Model (Smalltalk)
Business & Object Layer
Represents the pure object-oriented definition of an Omni Node.
Smalltalk's message-passing architecture mirrors distributed actor models perfectly."

Object subclass: #OmniNode
    instanceVariableNames: 'nodeId vramCapacity activeModels'
    classVariableNames: ''
    poolDictionaries: ''
    category: 'Omni-Ecosystem'!

!OmniNode methodsFor: 'initialization'!
initializeWithId: aString vram: anInteger
    nodeId := aString.
    vramCapacity := anInteger.
    activeModels := OrderedCollection new.
    ^self! !

!OmniNode methodsFor: 'accessing'!
id
    ^nodeId!

availableVram
    "Assume each active model consumes 4096MB for zero-mock calculation"
    | usedVram |
    usedVram := activeModels size * 4096.
    ^vramCapacity - usedVram! !

!OmniNode methodsFor: 'operations'!
deployModel: aModelName
    self availableVram < 4096 ifTrue: [
        self error: 'Insufficient VRAM to deploy model'.
    ].
    activeModels add: aModelName.
    Transcript show: 'Deployed ', aModelName, ' to node ', nodeId; cr.! !

"Usage Example:"
"| node |
 node := OmniNode new initializeWithId: 'omni-node-xyz' vram: 16384.
 node deployModel: 'Omni-LLaMA-8B'.
 Transcript show: 'Remaining VRAM: ', node availableVram printString."
