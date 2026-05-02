# OMNI Batch 5: Fix all remaining files with the universal "missing } + extra }" pattern
$ErrorActionPreference = "Continue"
$root = "c:\Users\IKYY\Downloads\Omni\src"
$fixed = 0

# Pattern: The file has a return statement inside an if/for that's missing its closing }
# Then the function has an extra } at the end
# We detect: any line that's just "return Err..(" or "return Ok..(" followed by empty line 
# then a return at the same or lower indent, then "}" twice

# Files to fix with the "add } after return, remove trailing }" pattern
$files = @(
    "compute\quicgo\omni_quic_go_packet_number_encryption.go",
    "compute\traefik\omni_traefik_router_rule_eval.go",
    "compute\vault\omni_vault_shamir_secret_share.go",
    "compute\nlp\iwslt_speech_to_text_translator.go",
    "events\catalyst\epoch_logger.go",
    "domain\financial\elliott_wave_oscillator.go"
)

foreach ($f in $files) {
    $file = "$root\$f"
    if (-not (Test-Path $file)) { continue }
    
    $lines = Get-Content $file
    $newLines = [System.Collections.ArrayList]@()
    $lastIdx = $lines.Count - 1
    
    # Find the last "}" "}" pattern and remove the second one
    # Also find lines where a return inside an if/for is missing closing }
    
    # Simple approach: find any "return" at 8-space indent followed by blank line then return at 4-space indent
    # The 8-space indent return is inside an if that's missing its closing }
    
    $addedBrace = $false
    $removedBrace = $false
    
    for ($i = 0; $i -lt $lines.Count; $i++) {
        $line = $lines[$i]
        
        # Check if current line is a return inside a block (8+ space indent) 
        # and the next non-empty line is a return at lower indent
        if (-not $addedBrace -and $line -match '^\s{8}return\s' -and $i + 1 -lt $lines.Count) {
            $nextLine = ""
            $nextIdx = $i + 1
            # Skip empty lines
            while ($nextIdx -lt $lines.Count -and $lines[$nextIdx].Trim() -eq "") {
                $nextIdx++
            }
            if ($nextIdx -lt $lines.Count -and $lines[$nextIdx] -match '^\treturn\s') {
                # This return is inside an if/for that's missing its }
                [void]$newLines.Add($line)
                [void]$newLines.Add("    }")
                $addedBrace = $true
                $fixed++
                Write-Host "  Added } after line $($i+1) in $f" -ForegroundColor Green
                continue
            }
        }
        
        # Remove trailing extra }
        if (-not $removedBrace -and $line.Trim() -eq "}" -and $i -gt 0) {
            $prevLine = $lines[$i-1].Trim()
            if ($prevLine -eq "}") {
                # This might be the extra } - check if it's the last one before EOF
                if ($i + 1 -ge $lines.Count -or $lines[$i+1].Trim() -eq "") {
                    $removedBrace = $true
                    Write-Host "  Removed extra } at line $($i+1) in $f" -ForegroundColor Yellow
                    continue
                }
            }
        }
        
        [void]$newLines.Add($line)
    }
    
    if ($addedBrace -or $removedBrace) {
        Set-Content -Path $file -Value ($newLines.ToArray()) -Encoding UTF8
    }
}

Write-Host "`n[BATCH 5] Processed files." -ForegroundColor Green
