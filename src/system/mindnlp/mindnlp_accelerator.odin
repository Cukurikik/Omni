// @omni-domain System Layer (MindNLP Accelerator)
// @omni-source mindspore/mindnlp
// @omni-description MindNLP Accelerator mimicking hardware abstraction in Odin.
// @omni-requirement zero-mock, monadic-error
package mindnlp_accelerator

OmniResult :: struct(T: typeid) { data: T, error: string, is_ok: bool }
ok :: proc(data: $T) -> OmniResult(T) { return OmniResult(T){data=data, error="", is_ok=true} }
err :: proc($T: typeid, msg: string) -> OmniResult(T) { return OmniResult(T){error=msg, is_ok=false} }

DeviceType :: enum { CPU, GPU, NPU }
TensorShape :: struct { dims: [4]int, ndim: int }

compute_tensor_memory :: proc(shape: TensorShape, dtype_bytes: int) -> OmniResult(int) {
    if shape.ndim <= 0 do return err(int, "Invalid ndim.")
    total := 1
    for i in 0..<shape.ndim { total *= shape.dims[i] }
    return ok(total * dtype_bytes)
}

select_device :: proc(tensor_size_mb: f64) -> OmniResult(DeviceType) {
    if tensor_size_mb <= 0 do return err(DeviceType, "Invalid size.")
    if tensor_size_mb > 2048 do return ok(DeviceType.NPU)
    if tensor_size_mb > 256 do return ok(DeviceType.GPU)
    return ok(DeviceType.CPU)
}
