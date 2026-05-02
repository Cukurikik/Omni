# OMNI Error Fix Script - Batch 1: Fix the most common patterns
# This script fixes the most pervasive error patterns across the codebase

$ErrorActionPreference = "Continue"
$root = "c:\Users\IKYY\Downloads\Omni\src"
$fixed = 0

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " OMNI ERROR FIX SCRIPT - BATCH 1" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ============================================================
# FIX 1: network/advanced_rag_api.go - Remove duplicate Err func, fix Error->Err, fix Ok usage
# ============================================================
Write-Host "`n[FIX 1] network/advanced_rag_api.go" -ForegroundColor Yellow
$content = @'
package network

import (
	"errors"
)

func CallRAGAPI(endpoint string) OmniResult[string] {
	if endpoint == "" {
		return ErrT[string](errors.New("empty endpoint"))
	}
	return OkT[string]("Success")
}
'@
Set-Content -Path "$root\network\advanced_rag_api.go" -Value $content -Encoding UTF8
$fixed++

# ============================================================
# FIX 2: network/alpharec_router.go
# ============================================================
Write-Host "[FIX 2] network/alpharec_router.go" -ForegroundColor Yellow
$content = @'
package network

import (
	"errors"
)

func RouteAlphaRecRequest(reqID string) OmniResult[bool] {
	if reqID == "" {
		return ErrT[bool](errors.New("empty request"))
	}
	return OkT[bool](true)
}
'@
Set-Content -Path "$root\network\alpharec_router.go" -Value $content -Encoding UTF8
$fixed++

# ============================================================
# FIX 3: network/anygpt_stream.go
# ============================================================
Write-Host "[FIX 3] network/anygpt_stream.go" -ForegroundColor Yellow
$file = "$root\network\anygpt_stream.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'return Ok\(true\)', 'return OkT[bool](true)'
    $c = $c -replace 'return Ok\(false\)', 'return OkT[bool](false)'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
}

# ============================================================
# FIX 4: network/autogpt_browser.go
# ============================================================
Write-Host "[FIX 4] network/autogpt_browser.go" -ForegroundColor Yellow
$file = "$root\network\autogpt_browser.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'return Ok\("Browsed"\)', 'return OkT[string]("Browsed")'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
}

# ============================================================
# FIX 5: network/blagpt_distributed.go
# ============================================================
Write-Host "[FIX 5] network/blagpt_distributed.go" -ForegroundColor Yellow
$file = "$root\network\blagpt_distributed.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'return Ok\(true\)', 'return OkT[bool](true)'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
}

# ============================================================
# FIX 6: network/deepseek_rpc.go
# ============================================================
Write-Host "[FIX 6] network/deepseek_rpc.go" -ForegroundColor Yellow
$file = "$root\network\deepseek_rpc.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'return Ok\(true\)', 'return OkT[bool](true)'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
}

# ============================================================
# FIX 7: network/knowledge_harvest_sync.go
# ============================================================
Write-Host "[FIX 7] network/knowledge_harvest_sync.go" -ForegroundColor Yellow
$file = "$root\network\knowledge_harvest_sync.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'return Ok\(true\)', 'return OkT[bool](true)'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
}

# ============================================================
# FIX 8: network/llm_starterkit_gateway.go
# ============================================================
Write-Host "[FIX 8] network/llm_starterkit_gateway.go" -ForegroundColor Yellow
$file = "$root\network\llm_starterkit_gateway.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'return Ok\(true\)', 'return OkT[bool](true)'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
}

# ============================================================
# FIX 9: network/meta_context_sync.go
# ============================================================
Write-Host "[FIX 9] network/meta_context_sync.go" -ForegroundColor Yellow
$file = "$root\network\meta_context_sync.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'return Ok\(true\)', 'return OkT[bool](true)'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
}

# ============================================================
# FIX 10: network/metagpt_bus.go
# ============================================================
Write-Host "[FIX 10] network/metagpt_bus.go" -ForegroundColor Yellow
$file = "$root\network\metagpt_bus.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'return Ok\(true\)', 'return OkT[bool](true)'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
}

# ============================================================
# FIX 11: network/mistral_haystack_router.go
# ============================================================
Write-Host "[FIX 11] network/mistral_haystack_router.go" -ForegroundColor Yellow
$file = "$root\network\mistral_haystack_router.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'return Ok\("Routed"\)', 'return OkT[string]("Routed")'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
}

# ============================================================
# FIX 12: network/multi_agent_ui_gateway.go
# ============================================================
Write-Host "[FIX 12] network/multi_agent_ui_gateway.go" -ForegroundColor Yellow
$file = "$root\network\multi_agent_ui_gateway.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'return Ok\("Routed to agent network"\)', 'return OkT[string]("Routed to agent network")'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
}

# ============================================================
# FIX 13: network/opengpt_server.go
# ============================================================
Write-Host "[FIX 13] network/opengpt_server.go" -ForegroundColor Yellow
$file = "$root\network\opengpt_server.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'return Ok\("Server started"\)', 'return OkT[string]("Server started")'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
}

# ============================================================
# FIX 14: network/qwq_api.go
# ============================================================
Write-Host "[FIX 14] network/qwq_api.go" -ForegroundColor Yellow
$file = "$root\network\qwq_api.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'return Ok\("Serving"\)', 'return OkT[string]("Serving")'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
}

# ============================================================
# FIX 15: network/agentsys_orchestrator_engine.go
# ============================================================
Write-Host "[FIX 15] network/agentsys_orchestrator_engine.go" -ForegroundColor Yellow
$file = "$root\network\agentsys_orchestrator_engine.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'return Ok\("Task Dispatched: " \+ task\)', 'return OkT[string]("Task Dispatched: " + task)'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
}

Write-Host "`n[BATCH 1] Fixed $fixed files." -ForegroundColor Green
