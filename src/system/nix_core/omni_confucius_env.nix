# Omni Confucius Build Env (Nix)
# System Layer: Reproducible environment for tool learning.
# Ref: mangopy/Confucius-tool-learning

{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = [ pkgs.python3 pkgs.python3Packages.torch ];
  shellHook = ''
    export OMNI_CONFUCIUS_MODE=curriculum
    echo "[OMNI] Confucius reproducible env activated."
  '';
}
