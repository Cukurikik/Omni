; ===============================================
; OMNI-LANG LLVM IR (Bare-Metal DNA)
; Target: x86_64-pc-windows-msvc / aarch64
; ===============================================

  %R1 = alloca i8, i32 1024
  %R2 = add i64 0, 42
  %R3 = call fast double @llvm.x86.avx.mul (<4 x double> %R1, <4 x double> %R2)
