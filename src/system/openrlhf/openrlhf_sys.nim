# OMNI Divine Memory Integration: Inspired by OpenRLHF
# System Layer - Nim systems metric gathering

import os, strutils

type
  OmniError = object
    code: int
    message: string

  OmniResult[T] = object
    case isOk: bool
    of true:
      value: T
    of false:
      error: OmniError

const MAX_CPU_TEMP_C = 95.0

proc getSystemCpuTemp(): OmniResult[float] =
  # Zero-mock: Reads from Linux sysfs directly
  const tempPath = "/sys/class/thermal/thermal_zone0/temp"
  
  if not fileExists(tempPath):
    return OmniResult[float](isOk: false, error: OmniError(code: 404, message: "Thermal zone not found."))
    
  try:
    let rawTemp = readFile(tempPath).strip()
    let tempC = parseFloat(rawTemp) / 1000.0
    
    if tempC > MAX_CPU_TEMP_C:
      return OmniResult[float](isOk: false, error: OmniError(code: 413, message: "Thermal throttling limit reached."))
      
    return OmniResult[float](isOk: true, value: tempC)
  except ValueError:
    return OmniResult[float](isOk: false, error: OmniError(code: 500, message: "Invalid thermal data format."))

when isMainModule:
  let tempRes = getSystemCpuTemp()
  if tempRes.isOk:
    echo "Current Temp: ", tempRes.value, "°C"
  else:
    echo "Error: ", tempRes.error.message
