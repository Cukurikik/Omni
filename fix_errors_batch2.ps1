# OMNI Error Fix Script - Batch 2: go_core router Err->Error field fixes + more
$ErrorActionPreference = "Continue"
$root = "c:\Users\IKYY\Downloads\Omni\src"
$fixed = 0

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " OMNI ERROR FIX SCRIPT - BATCH 2" -ForegroundColor Cyan
Write-Host " go_core routers + concurrency fixes" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# ============================================================
# Pattern A: go_core router files - all use Err but struct has Error
# Fix: Replace Err with Error in struct literals
# ============================================================
$routerFiles = @(
    "omni_advanced_rag_router.go",
    "omni_alpharec_router.go",
    "omni_autogen_router.go",
    "omni_axolotl_trainer_router.go",
    "omni_blagpt_router.go",
    "omni_dspy_router.go",
    "omni_flora_opt_router.go",
    "omni_gpt4all_unity_router.go",
    "omni_guidance_router.go",
    "omni_icl_ceil_router.go",
    "omni_kg_harvest_router.go",
    "omni_langchain_prefect_router.go",
    "omni_llama_index_router.go",
    "omni_llm_starterkit_router.go",
    "omni_llmebench_router.go",
    "omni_lm_eval_router.go",
    "omni_m3exam_router.go",
    "omni_meta_context_router.go",
    "omni_mistral_haystack_router.go",
    "omni_multi_agent_ui_router.go",
    "omni_oceangpt_router.go",
    "omni_ollama_dist_router.go",
    "omni_open_gpt_router.go",
    "omni_peft_lora_router.go",
    "omni_reclm_router.go",
    "omni_reflect_router.go",
    "omni_table_survey_router.go",
    "omni_trl_ppo_router.go",
    "omni_uot_router.go",
    "omni_vllm_engine_router.go"
)

foreach ($f in $routerFiles) {
    $file = "$root\network\go_core\$f"
    if (Test-Path $file) {
        $c = Get-Content $file -Raw
        # Replace ", Err:" with ", Error:" in struct literals
        $c = $c -replace ', Err:', ', Error:'
        # Replace "{Err:" (start of struct) with "{Error:"
        $c = $c -replace '\{Err:', '{Error:'
        # Fix "Err: nil" to "Error: nil"
        $c = $c -replace 'Err: nil', 'Error: nil'
        Set-Content -Path $file -Value $c -Encoding UTF8
        $fixed++
        Write-Host "  Fixed $f" -ForegroundColor Green
    }
}

# ============================================================
# Pattern B: go_core autonomous_intel - multiple issues
# ============================================================
Write-Host "`n[Pattern B] omni_autonomous_intel.go" -ForegroundColor Yellow
$file = "$root\network\go_core\omni_autonomous_intel.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    # Fix Err -> Error in struct literals
    $c = $c -replace ', Err:', ', Error:'
    $c = $c -replace '\{Err:', '{Error:'
    # Remove unused "time" import won't hurt if it's actually used
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed" -ForegroundColor Green
}

# ============================================================
# Pattern C: concurrency files with "unknown field Err" in various structs
# ============================================================
Write-Host "`n[Pattern C] Concurrency struct field fixes" -ForegroundColor Yellow

# diffusers/pipeline_worker.go - GenResult has Err field issue
$file = "$root\concurrency\diffusers\pipeline_worker.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'Err:', 'Error:'
    $c = $c -replace '\.Err\b', '.Error'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed diffusers/pipeline_worker.go" -ForegroundColor Green
}

# haiku/gradient_worker.go - GradientResult has no Err field
$file = "$root\concurrency\haiku\gradient_worker.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'Err:', 'Error:'
    $c = $c -replace 'res\.Err\b', 'res.Error'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed haiku/gradient_worker.go" -ForegroundColor Green
}

# higgsfield/fault_tolerance_monitor.go - NodeHealth has no Err field
$file = "$root\concurrency\higgsfield\fault_tolerance_monitor.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'Err:', 'Error:'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed higgsfield/fault_tolerance_monitor.go" -ForegroundColor Green
}

# towhee/pipeline_worker.go - ProcessingResult has no Err field
$file = "$root\concurrency\towhee\pipeline_worker.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'Err:', 'Error:'
    $c = $c -replace 'res\.Err\b', 'res.Error'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed towhee/pipeline_worker.go" -ForegroundColor Green
}

# events/automl/training_metrics.go - EmitResult has no Err field
$file = "$root\events\automl\training_metrics.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'Err:', 'Error:'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed events/automl/training_metrics.go" -ForegroundColor Green
}

# ============================================================
# Pattern D: "unknown field Error" - struct uses Err but code uses Error
# ============================================================
Write-Host "`n[Pattern D] Struct Error->Err fixes" -ForegroundColor Yellow

# network/bentoml_http_runner.go
$file = "$root\network\bentoml_http_runner.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'Error:', 'Err:'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed bentoml_http_runner.go" -ForegroundColor Green
}

# network/langchain_api_gateway.go
$file = "$root\network\langchain_api_gateway.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'Error:', 'Err:'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed langchain_api_gateway.go" -ForegroundColor Green
}

# network/prompt_proxy.go
$file = "$root\network\prompt_proxy.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'Error:', 'Err:'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed prompt_proxy.go" -ForegroundColor Green
}

# network/tragx_rag_client.go
$file = "$root\network\tragx_rag_client.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'Error:', 'Err:'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed tragx_rag_client.go" -ForegroundColor Green
}

# go_core/omni_perplexity_stream_engine.go - ResultStreamMeta has no Error field
$file = "$root\network\go_core\omni_perplexity_stream_engine.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'Error:', 'Err:'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed omni_perplexity_stream_engine.go" -ForegroundColor Green
}

# go_core/omni_videodb_engine.go - ResultVideoMeta has no Error field
$file = "$root\network\go_core\omni_videodb_engine.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace 'Error:', 'Err:'
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed omni_videodb_engine.go" -ForegroundColor Green
}

# ============================================================
# Pattern E: Unused imports
# ============================================================
Write-Host "`n[Pattern E] Unused import fixes" -ForegroundColor Yellow

# concurrency/b_tree_index/lock_coupling.go - "fmt" imported and not used
$file = "$root\concurrency\b_tree_index\lock_coupling.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace '^\s*"fmt"\s*\n', ''
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed b_tree_index/lock_coupling.go" -ForegroundColor Green
}

# concurrency/cif_broker/cif_broker.go - "errors" imported and not used
$file = "$root\concurrency\cif_broker\cif_broker.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace '\s*"errors"\s*\n', "`n"
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed cif_broker/cif_broker.go" -ForegroundColor Green
}

# concurrency/openstorypp_broker/openstorypp_broker.go - "errors" unused
$file = "$root\concurrency\openstorypp_broker\openstorypp_broker.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace '\s*"errors"\s*\n', "`n"
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed openstorypp_broker/openstorypp_broker.go" -ForegroundColor Green
}

# concurrency/stock_valuation/stock_valuation.go - "errors" unused
$file = "$root\concurrency\stock_valuation\stock_valuation.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace '\s*"errors"\s*\n', "`n"
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed stock_valuation/stock_valuation.go" -ForegroundColor Green
}

# concurrency/yesbut_stream/yesbut_stream.go - "errors" unused
$file = "$root\concurrency\yesbut_stream\yesbut_stream.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace '\s*"errors"\s*\n', "`n"
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed yesbut_stream/yesbut_stream.go" -ForegroundColor Green
}

# concurrency/medical_qa/medical_qa_embedding_client.go - "time" unused
$file = "$root\concurrency\medical_qa\medical_qa_embedding_client.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace '\s*"time"\s*\n', "`n"
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed medical_qa/medical_qa_embedding_client.go" -ForegroundColor Green
}

# concurrency/memory/tcmalloc_thread_cache.go - "time" unused
$file = "$root\concurrency\memory\tcmalloc_thread_cache.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace '\s*"time"\s*\n', "`n"
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed memory/tcmalloc_thread_cache.go" -ForegroundColor Green
}

# events/swanlab/log_stream.go - "log" unused
$file = "$root\events\swanlab\log_stream.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace '\s*"log"\s*\n', "`n"
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed events/swanlab/log_stream.go" -ForegroundColor Green
}

# go_core/omni_animelinks_engine.go - "log" unused
$file = "$root\network\go_core\omni_animelinks_engine.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace '\s*"log"\s*\n', "`n"
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed go_core/omni_animelinks_engine.go" -ForegroundColor Green
}

# go_core/omni_autonomous_intel.go - "time" unused
$file = "$root\network\go_core\omni_autonomous_intel.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    $c = $c -replace '\s*"time"\s*\n', "`n"
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed go_core/omni_autonomous_intel.go" -ForegroundColor Green
}

# system/fs/pdf_text_extraction_engine.go - "err" declared unused
$file = "$root\system\fs\pdf_text_extraction_engine.go"
if (Test-Path $file) {
    $c = Get-Content $file -Raw
    # Replace err unused by using _
    $c = $c -replace 'err :=', '_ ='
    Set-Content -Path $file -Value $c -Encoding UTF8
    $fixed++
    Write-Host "  Fixed system/fs/pdf_text_extraction_engine.go" -ForegroundColor Green
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "[BATCH 2] Fixed $fixed files." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
