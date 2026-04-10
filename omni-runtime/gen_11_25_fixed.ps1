$packages = @(
    "omni-fs-core", "omni-fs-async", "omni-path", "omni-os",
    "omni-process", "omni-child", "omni-tty", "omni-stream-io",
    "omni-readline", "omni-net-tcp", "omni-net-udp", "omni-dns",
    "omni-crypto-hash", "omni-crypto-tls", "omni-compress"
)
$mods = "c:\Users\IKYY\Downloads\Omni\omni-runtime\omni_modules"
foreach ($pkg in $packages) {
    # Create directories
    $dir = "$mods\$pkg"
    if (!(Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
    if (!(Test-Path "$dir\src")) { New-Item -ItemType Directory -Force -Path "$dir\src" | Out-Null }
    if (!(Test-Path "$dir\tests")) { New-Item -ItemType Directory -Force -Path "$dir\tests" | Out-Null }
    if (!(Test-Path "$dir\examples")) { New-Item -ItemType Directory -Force -Path "$dir\examples" | Out-Null }

    # toml
    $safe = $pkg.Replace("-", "_")
    Set-Content -Path "$dir\Omnifile.toml" -Value @"
[package]
name = "$pkg"
version = "1.0.0"
[dependencies]
omni-std = "^2.0"
[publish]
registry = "https://nexus.omniframework.dev"
tier = "free"
"@ -Encoding UTF8

    # readme
    Set-Content -Path "$dir\README.md" -Value "# $pkg v1.0.0`nNative OS bindings for OMNI." -Encoding UTF8

    # src
    Set-Content -Path "$dir\src\lib.omni" -Value @"
/// [OMNI] $pkg
export interface $($safe)_sys { fn init() -> bool; }
"@ -Encoding UTF8

    # test
    Set-Content -Path "$dir\tests\unit.omni" -Value "test('$pkg', fn() {})" -Encoding UTF8

    Write-Host "Re-generated: $pkg"
}
