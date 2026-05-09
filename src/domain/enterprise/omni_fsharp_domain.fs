// OMNI Domain Layer: Immutable functional models for Enterprise Healthcare/Finance
// F# implementation defining strict, monadic business types.

module Omni.Business.CoreModels

open System

// Strictly typed primitives to prevent primitive obsession
type PatientId = PatientId of Guid
type EncounterId = EncounterId of Guid
type RiskScore = RiskScore of float

// Monadic error handling representation
type DomainError =
    | InvalidData of string
    | UnauthorizedAccess of string
    | OmniEngineTimeout of string

// Result Monad defined implicitly via standard F# Result type
// Result<'T, DomainError>

type VoxelData = {
    Dimensions: int * int * int
    RawBuffer: byte array // Pinned later at the C# boundary
}

type PatientEncounter = {
    Id: EncounterId
    Patient: PatientId
    Timestamp: DateTime
    Scans: VoxelData option
}

let createEncounter (patientId: Guid) =
    let encId = EncounterId (Guid.NewGuid())
    let patId = PatientId patientId
    Ok { Id = encId; Patient = patId; Timestamp = DateTime.UtcNow; Scans = None }

let attachScan (encounter: PatientEncounter) (dimX: int, dimY: int, dimZ: int) (buffer: byte array) =
    if buffer.Length <> (dimX * dimY * dimZ) then
        Error (InvalidData "Buffer length does not match provided dimensions.")
    else
        let scan = { Dimensions = (dimX, dimY, dimZ); RawBuffer = buffer }
        Ok { encounter with Scans = Some scan }

let dispatchToOmni (encounter: PatientEncounter) : Result<RiskScore, DomainError> =
    match encounter.Scans with
    | None -> Error (InvalidData "Cannot analyze encounter without voxel scans.")
    | Some scan -> 
        // Simulated bridge call to C# P/Invoke layer
        printfn "OMNI F# Dispatch: Sending %A buffer to Universal Engine." scan.Dimensions
        Ok (RiskScore 0.85)
