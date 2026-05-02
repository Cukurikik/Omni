# OMNI Error Fix Script - Batch 3: Fix premature for-loop closing braces
# Pattern: for x := range channel { if check { ... continue } } <- this } closes the loop too early
# Code after it references the loop variable which is now out of scope

$ErrorActionPreference = "Continue"
$root = "c:\Users\IKYY\Downloads\Omni\src"
$fixed = 0

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " OMNI ERROR FIX SCRIPT - BATCH 3" -ForegroundColor Cyan
Write-Host " Premature for-loop close fixes" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Files with the premature for-loop close pattern
# The pattern is: continue\n\t\t}\n}\n  <-- extra } closes loop, remaining code uses loop var

$files = @(
    "concurrency\auto_simulator\sensor_streamer.go",
    "concurrency\causal_infer\inference_pool.go",
    "concurrency\code_representation\repo_indexer.go",
    "concurrency\cvcuda\frame_worker_pool.go",
    "concurrency\dataflow_etl\pipeline_streamer.go",
    "concurrency\dlmusic\audio_stream_pool.go",
    "concurrency\fedml\grpc_bridge.go",
    "concurrency\hyper_ml\compute_pool.go",
    "concurrency\malware_detect\apk_worker.go",
    "concurrency\medical_imaging\slice_worker.go",
    "concurrency\ml_metrics\metric_streamer.go",
    "concurrency\netquant\calibration_pool.go",
    "concurrency\openinterface\event_loop_worker.go",
    "concurrency\scientific_computing\compute_streamer.go",
    "concurrency\textembedding\document_worker_pool.go",
    "concurrency\perplexity_go\search_pool.go",
    "concurrency\promptml\build_worker_pool.go"
)

foreach ($f in $files) {
    $file = "$root\$f"
    if (Test-Path $file) {
        $lines = Get-Content $file
        $newLines = @()
        $skipNextCloseBrace = $false
        
        for ($i = 0; $i -lt $lines.Count; $i++) {
            $line = $lines[$i]
            $prevLine = if ($i -gt 0) { $lines[$i-1] } else { "" }
            $prevPrevLine = if ($i -gt 1) { $lines[$i-2] } else { "" }
            
            # Detect the problematic pattern: line after "continue" + closing brace that is just "}"
            # followed by empty line or code that uses the loop variable
            if ($line -match '^\}$' -and $prevLine -match '^\t\t\}$' -and $prevPrevLine -match 'continue') {
                # Skip this premature closing brace
                Write-Host "  Skipping premature } at line $($i+1) in $f" -ForegroundColor Gray
                continue
            }
            
            $newLines += $line
        }
        
        Set-Content -Path $file -Value $newLines -Encoding UTF8
        $fixed++
        Write-Host "  Fixed $f" -ForegroundColor Green
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "[BATCH 3] Fixed $fixed files." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
