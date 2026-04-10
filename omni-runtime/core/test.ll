; ===============================================
; OMNI-PRIME The Realism Protocol (LLVM IR Direct Emit)
; Target: x86_64-pc-windows-msvc / aarch64
; ===============================================

declare void @omni_spawn(i8* %task_ptr)
declare i64 @omni_await(i8* %task_ptr)
declare void @omni_polyglot_dispatch(i8* %lang, i8* %code)

define i32 @main() {
entry:
  ; let message = ...
  ; [Polyglot: rust]
  call void @omni_polyglot_dispatch(i8* null, i8* null)
  ; [Polyglot: go]
  call void @omni_polyglot_dispatch(i8* null, i8* null)
  ret i32 0
}
