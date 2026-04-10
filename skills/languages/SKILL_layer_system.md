# SKILL: SYSTEM LAYER — C, C++, Rust
**File:** `languages/SKILL_layer_system.md`  
**Layer:** Languages  
**Bahasa:** C · C++ · Rust

---

## Peran Domain

System Layer bertanggung jawab atas semua yang berhubungan dengan hardware, memori, kriptografi, dan akses kernel. Ini adalah fondasi dari seluruh OMNI Framework.

| Bahasa | Keunggulan | Kapan Digunakan |
|--------|-----------|-----------------|
| **C** | Zero overhead, universal FFI, kernel ABI | Saat butuh interop dengan OS atau library C eksternal |
| **C++** | Template metaprogramming, RAII, GPU via CUDA/HIP | Saat butuh generic algoritma atau komputasi GPU |
| **Rust** | Memory-safe tanpa GC, ownership model, async-safe | Default pilihan untuk semua kode system yang baru |

---

## Idiom OMNI untuk System Layer

```omni
// C: FFI binding ke library eksternal
extern "omni-c" fn openssl_encrypt(
  key: *const u8,
  data: *const u8,
  len: usize
) -> *mut u8

// C++: Template untuk generic data structure
@cpp_template<T: Comparable>
struct SortedBuffer {
  data: Vec<T>
  fn insert(item: T) -> Result<(), BufferError>
}

// Rust: Memory-safe concurrent data access
fn process_shared_data<'a>(
  data: &'a [u8],
  lock: &'a Mutex<ProcessorState>
) -> Result<ProcessedOutput, SystemError> {
  let state = lock.lock().map_err(|_| SystemError::LockPoisoned)?
  let result = unsafe { raw_process(data.as_ptr(), data.len()) }
  Ok(ProcessedOutput::from_raw(result))
}
```

---

## Pola Alokasi Memori Aman

```omni
// Selalu gunakan unsafe_zone yang terisolasi
unsafe_zone "crypto_buffer" {
  let key_ptr: *mut u8 = c::malloc(32)
  defer {
    c::memset(key_ptr, 0, 32)  // zero-fill sebelum free (keamanan)
    c::free(key_ptr)
  }

  // Gunakan Rust wrapper untuk operasi aman
  let key_slice = rust::slice::from_raw_parts_mut(key_ptr, 32)
  fill_random_bytes(key_slice)?
}
// key_ptr otomatis di-free dan di-zero di sini
```

---

## eBPF Kernel Bypass (untuk HFT & networking)

```omni
@ebpf_kernel
fn intercept_packet(ctx: XdpContext) -> XdpAction {
  let eth = ctx.parse::<EthernetHeader>()?
  if eth.ethertype == ETHERTYPE_IP {
    let ip = ctx.parse::<IpHeader>()?
    if ip.protocol == IPPROTO_TCP {
      return XdpAction::Pass  // proses di userspace
    }
  }
  XdpAction::Drop
}
```

---

## Aturan System Layer

1. Semua unsafe block HARUS ada komentar penjelasan mengapa unsafe diperlukan
2. Setiap alokasi manual HARUS ada pasangan deallokasi dengan `defer`
3. Semua pointer yang berisi data sensitif HARUS di-zero-fill sebelum free
4. Jangan expose raw pointer ke layer lain — bungkus dengan Rust wrapper dulu

---

*ANTIGRAVITY Skills — languages/SKILL_layer_system.md*
