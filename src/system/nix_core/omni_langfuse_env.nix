# Omni Langfuse Environment (Nix)
# System Layer: Perfectly reproducible build environment for Langfuse telemetry ingestion.

{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.go
    pkgs.protobuf
    pkgs.kafka
  ];

  shellHook = ''
    export OMNI_LANGFUSE_STRICT_MODE=1
    export OMNI_TELEMETRY_PORT=4317
    echo "[OMNI] Langfuse reproducible environment activated."
  '';
}
