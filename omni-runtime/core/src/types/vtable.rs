/// V-Table (Virtual Method Table) merepresentasikan fungsi kelas Polimorfik
pub struct VTable {
    pub type_id: u64,
    pub execute_fn: fn(*const ()),
}

/// Pointer Gemuk (Fat Pointer) penyimpan alamat Data + alamat V-Table
pub struct OmniFatPointer {
    pub data_ptr: *const (),
    pub vtable_ptr: *const VTable,
}

impl OmniFatPointer {
    pub fn new(data: *const (), vtable: *const VTable) -> Self {
        println!("[POLYMORPH] 🧬 Mengkonversi Tipe Statis menjadi Tipe Dinamis (Fat Pointer)!");
        Self {
            data_ptr: data,
            vtable_ptr: vtable,
        }
    }

    pub fn dispatch(&self) {
        if self.data_ptr.is_null() || self.vtable_ptr.is_null() {
            println!("[POLYMORPH] ⚠️ Invalid Dispatch!");
            return;
        }
        
        unsafe {
            println!("[POLYMORPH] ⚡ Dynamic Dispatch diinjeksi via O(1) Memory Offset di Register CPU!");
            let v_table = &*self.vtable_ptr;
            (v_table.execute_fn)(self.data_ptr);
        }
    }
}
