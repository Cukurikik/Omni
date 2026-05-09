# @omni-layer Infrastructure | @omni-lang PowerShell | @omni-batch 18 | @omni-semester 16
# @omni-description PowerShell deployment and monitoring toolkit for OMNI
# transformer inference cluster on Windows/Azure environments.

function Deploy-OmniTransformerModel {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ModelId,
        [string]$ModelPath,
        [string]$TargetEndpoint = "http://localhost:8080",
        [int]$MaxBatchSize = 32,
        [int]$TimeoutSeconds = 300
    )

    Write-Host "[OMNI] Deploying model: $ModelId" -ForegroundColor Cyan

    if (-not (Test-Path $ModelPath)) {
        throw "Model path not found: $ModelPath"
    }

    $modelInfo = @{
        model_id = $ModelId
        model_path = $ModelPath
        max_batch_size = $MaxBatchSize
        timestamp = (Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
    }

    $body = $modelInfo | ConvertTo-Json -Depth 5
    try {
        $response = Invoke-RestMethod -Uri "$TargetEndpoint/api/models/deploy" `
            -Method Post -Body $body -ContentType "application/json" `
            -TimeoutSec $TimeoutSeconds
        Write-Host "[OMNI] Model deployed successfully: $($response.status)" -ForegroundColor Green
        return $response
    } catch {
        Write-Error "[OMNI] Deployment failed: $_"
        throw
    }
}

function Get-OmniTransformerMetrics {
    [CmdletBinding()]
    param(
        [string]$Endpoint = "http://localhost:8080",
        [string[]]$ModelIds = @(),
        [int]$LastMinutes = 60
    )

    $uri = "$Endpoint/api/metrics?last_minutes=$LastMinutes"
    if ($ModelIds.Count -gt 0) {
        $uri += "&models=" + ($ModelIds -join ",")
    }

    try {
        $metrics = Invoke-RestMethod -Uri $uri -Method Get -TimeoutSec 30
        $report = @()
        foreach ($model in $metrics.models) {
            $report += [PSCustomObject]@{
                ModelId      = $model.model_id
                AvgLatencyMs = [math]::Round($model.avg_latency_ms, 2)
                P95LatencyMs = [math]::Round($model.p95_latency_ms, 2)
                Throughput   = [math]::Round($model.throughput_rps, 1)
                TotalRequests = $model.total_requests
                ErrorRate    = [math]::Round($model.error_rate * 100, 2)
                Status       = $model.status
            }
        }
        return $report | Format-Table -AutoSize
    } catch {
        Write-Warning "[OMNI] Failed to fetch metrics: $_"
        return $null
    }
}

function Test-OmniTransformerHealth {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string[]]$Endpoints,
        [int]$TimeoutSec = 10
    )

    $results = @()
    foreach ($ep in $Endpoints) {
        $start = Get-Date
        try {
            $response = Invoke-RestMethod -Uri "$ep/health" -Method Get -TimeoutSec $TimeoutSec
            $latency = ((Get-Date) - $start).TotalMilliseconds
            $results += [PSCustomObject]@{
                Endpoint = $ep
                Status   = "Healthy"
                LatencyMs = [math]::Round($latency, 1)
                Models   = $response.loaded_models
                GPU      = $response.gpu_available
            }
        } catch {
            $results += [PSCustomObject]@{
                Endpoint = $ep
                Status   = "Unhealthy"
                LatencyMs = -1
                Models   = 0
                GPU      = $false
            }
        }
    }
    return $results
}

function Invoke-OmniInference {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)]
        [string]$ModelId,
        [Parameter(Mandatory)]
        [string]$Text,
        [string]$Endpoint = "http://localhost:8080",
        [int]$MaxTokens = 128,
        [float]$Temperature = 0.7
    )

    $body = @{
        model_id = $ModelId
        text = $Text
        max_tokens = $MaxTokens
        temperature = $Temperature
    } | ConvertTo-Json

    $start = Get-Date
    $response = Invoke-RestMethod -Uri "$Endpoint/api/inference" `
        -Method Post -Body $body -ContentType "application/json"
    $latency = ((Get-Date) - $start).TotalMilliseconds

    return [PSCustomObject]@{
        ModelId    = $ModelId
        Output     = $response.output
        TokenCount = $response.token_count
        LatencyMs  = [math]::Round($latency, 1)
        Confidence = $response.confidence
    }
}
