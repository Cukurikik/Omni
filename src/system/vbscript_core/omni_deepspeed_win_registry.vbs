' Omni DeepSpeed Windows Registry (VBScript)
' System Layer: Deterministic registry initialization for local DeepSpeed sharding configurations on Windows.

Option Explicit

Dim WshShell, RegistryPath
Set WshShell = WScript.CreateObject("WScript.Shell")

RegistryPath = "HKCU\Software\OmniFramework\DeepSpeed\"

' Strictly enforce deterministic config
WshShell.RegWrite RegistryPath & "ZeRO_Stage", 3, "REG_DWORD"
WshShell.RegWrite RegistryPath & "Offload_Optimizer", 1, "REG_DWORD"
WshShell.RegWrite RegistryPath & "Strict_Determinism", 1, "REG_DWORD"

WScript.Echo "OMNI_SYS: DeepSpeed registry bounds strictly enforced."
