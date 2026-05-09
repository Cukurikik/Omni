# ==============================================================================
# OMNI NEXUS - POLYGLOT ENVIRONMENT ORCHESTRATOR
# Version: 3.1.0-OMNI-MOTHER-NEXUS
# ==============================================================================

Write-Host "--- INITIALIZING OMNI NEXUS POLYGLOT ENVIRONMENT ---" -ForegroundColor Cyan

function Check-Tool($cmd, $name, $installHint) {
    $command = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($command) {
        $version = ""
        try {
            if ($cmd -eq "rustc") { $version = (rustc --version) }
            elseif ($cmd -eq "go") { $version = (go version) }
            elseif ($cmd -eq "python") { $version = (python --version) }
            elseif ($cmd -eq "node") { $version = (node --version) }
        } catch {}
        Write-Host "[FOUND] $name $version" -ForegroundColor Green
        return $true
    } else {
        Write-Host "[MISSING] $name - Hint: $installHint" -ForegroundColor Yellow
        return $false
    }
}

# --- SYSTEM LAYER ---
Check-Tool "rustc" "Rust" "rustup.rs"
Check-Tool "zig" "Zig" "ziglang.org"
Check-Tool "odin" "Odin" "odin-lang.org"
Check-Tool "cl" "MSVC C/C++" "Visual Studio Build Tools"
Check-Tool "nasm" "NASM (Assembly)" "nasm.us"

# --- CONCURRENCY & NETWORK ---
Check-Tool "go" "Go" "golang.org"
Check-Tool "elixir" "Elixir" "elixir-lang.org"
Check-Tool "erl" "Erlang" "erlang.org"
Check-Tool "gleam" "Gleam" "gleam.run"
Check-Tool "ballerina" "Ballerina" "ballerina.io"

# --- COMPUTE & DATA ---
Check-Tool "python" "Python" "python.org"
Check-Tool "julia" "Julia" "julialang.org"
Check-Tool "R" "R" "r-project.org"
Check-Tool "mojo" "Mojo" "modular.com/mojo"

# --- INTERFACE LAYER ---
Check-Tool "dart" "Dart" "dart.dev"
Check-Tool "flutter" "Flutter" "flutter.dev"
Check-Tool "node" "Node.js" "nodejs.org"
Check-Tool "bun" "Bun" "bun.sh"
Check-Tool "deno" "Deno" "deno.land"

# --- BUSINESS & DATA ---
Check-Tool "dotnet" ".NET / C#" "dotnet.microsoft.com"
Check-Tool "ruby" "Ruby" "ruby-lang.org"
Check-Tool "php" "PHP" "php.net"
Check-Tool "composer" "Composer" "getcomposer.org"
Check-Tool "sqlcmd" "SQL Tools" "learn.microsoft.com"

# --- INFRA & SECURITY ---
Check-Tool "terraform" "Terraform" "terraform.io"
Check-Tool "pulumi" "Pulumi" "pulumi.com"
Check-Tool "opa" "Open Policy Agent" "openpolicyagent.org"

# --- BLOCKCHAIN ---
Check-Tool "solc" "Solidity" "soliditylang.org"

# --- PYTHON VIRTUAL ENVIRONMENT SYNC ---
$venvPath = Join-Path (Get-Location) ".venv"
$pipPath = Join-Path $venvPath "Scripts\pip.exe"
$reqPath = Join-Path (Get-Location) "src\compute\python_core\requirements.txt"

if (Test-Path $venvPath) {
    Write-Host "--- SYNCING PYTHON COMPUTE LAYER (.venv) ---" -ForegroundColor Cyan
    if (Test-Path $reqPath) {
        & $pipPath install -r $reqPath
    } else {
        Write-Host "[ERROR] requirements.txt not found at $reqPath" -ForegroundColor Red
    }
} else {
    Write-Host "[WARNING] .venv not found. Run: py -3.12 -m venv .venv" -ForegroundColor Yellow
}

Write-Host "--- OMNI NEXUS SCAN COMPLETE ---" -ForegroundColor Cyan
