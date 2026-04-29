# Omni FLASK Eval Runner (PowerShell)
# CLI/Scripting Layer: Cross-platform runner for evaluation scripts.

param(
    [Parameter(Mandatory=$true)]
    [string]$ModelId,
    [Parameter(Mandatory=$true)]
    [string]$SkillSet
)

try {
    if ([string]::IsNullOrWhiteSpace($ModelId)) {
        throw "ModelId cannot be null or whitespace."
    }
    
    # Deterministic output for script layer
    $result = @{
        Success = $true
        ModelId = $ModelId
        SkillSet = $SkillSet
        ExecutionTimestamp = [datetime]::UtcNow.ToString("o")
        EvalHash = "ps-omni-" + $ModelId.GetHashCode()
    }
    
    Write-Output ($result | ConvertTo-Json -Compress)
} catch {
    $errorState = @{
        Success = $false
        Error = $_.Exception.Message
    }
    Write-Output ($errorState | ConvertTo-Json -Compress)
    exit 1
}
