#![allow(dead_code)]
// ==========================================
// 📐 STRUCT LAYOUT ENGINE — Memory Layout Calculator
// ==========================================
// Menghitung posisi, padding, dan alignment setiap field
// dalam struct ABI-stable, mengikuti aturan C ABI.
//
// ATURAN C ABI (berlaku untuk 15 bahasa):
//   1. Field di-align ke kelipatan alignment type-nya
//   2. Struct alignment = alignment terbesar dari semua field
//   3. Total size = kelipatan struct alignment (tail padding)
//   4. Field TIDAK pernah di-reorder (sesuai deklarasi)
//
// CONTOH:
//   struct Account {
//     id: StringPtr     // offset 0, size 8, align 8
//     balance: Float64  // offset 8, size 8, align 8
//     is_frozen: Boolean // offset 16, size 1, align 1
//     // padding: 7 bytes (align to 8)
//   }
//   // Total: 24 bytes (3 * 8-byte alignment)
// ==========================================

use super::ABIField;

/// Computed layout for a single field
#[derive(Debug, Clone)]
pub struct FieldLayout {
    pub name: String,
    pub offset: usize,
    pub size: usize,
    pub alignment: usize,
    pub padding_before: usize,
}

/// Computed layout for the entire struct
#[derive(Debug, Clone)]
pub struct StructLayout {
    pub fields: Vec<FieldLayout>,
    pub total_size: usize,
    pub alignment: usize,
    pub padding_bytes: usize,
}

/// Type size information
#[derive(Debug, Clone)]
pub struct TypeSize {
    pub size: usize,
    pub alignment: usize,
}

/// Compute C ABI-compatible struct layout
pub fn compute_c_layout(fields: &[ABIField]) -> StructLayout {
    let mut field_layouts = Vec::new();
    let mut current_offset = 0usize;
    let mut max_alignment = 1usize;
    let mut total_padding = 0usize;

    for field in fields {
        let size = field.field_type.size();
        let align = field.field_type.alignment();

        // Update max alignment
        if align > max_alignment {
            max_alignment = align;
        }

        // Calculate padding needed for alignment
        let padding = if current_offset % align != 0 {
            align - (current_offset % align)
        } else {
            0
        };

        current_offset += padding;
        total_padding += padding;

        field_layouts.push(FieldLayout {
            name: field.name.clone(),
            offset: current_offset,
            size,
            alignment: align,
            padding_before: padding,
        });

        current_offset += size;
    }

    // Tail padding to align struct size to max alignment
    let tail_padding = if current_offset % max_alignment != 0 {
        max_alignment - (current_offset % max_alignment)
    } else {
        0
    };
    total_padding += tail_padding;
    current_offset += tail_padding;

    StructLayout {
        fields: field_layouts,
        total_size: current_offset,
        alignment: max_alignment,
        padding_bytes: total_padding,
    }
}

/// Compute packed layout (no padding, #pragma pack(1))
pub fn compute_packed_layout(fields: &[ABIField]) -> StructLayout {
    let mut field_layouts = Vec::new();
    let mut current_offset = 0usize;

    for field in fields {
        let size = field.field_type.size();
        let align = field.field_type.alignment();

        field_layouts.push(FieldLayout {
            name: field.name.clone(),
            offset: current_offset,
            size,
            alignment: align,
            padding_before: 0,
        });

        current_offset += size;
    }

    StructLayout {
        fields: field_layouts,
        total_size: current_offset,
        alignment: 1,
        padding_bytes: 0,
    }
}

/// Generate LLVM IR type definition from layout
pub fn layout_to_llvm_ir(name: &str, layout: &StructLayout) -> String {
    let mut fields = Vec::new();
    let mut last_end = 0;

    for fl in &layout.fields {
        // Insert padding array if needed
        if fl.offset > last_end {
            let pad = fl.offset - last_end;
            fields.push(format!("[{} x i8]", pad));
        }
        
        let llvm_type = match fl.size {
            1 => "i8",
            2 => "i16",
            4 => "i32",
            8 => "i64",
            16 => "[2 x i64]",
            24 => "{{ i8*, i64, i64 }}", // OMNI string
            _ => "i8",
        };
        fields.push(llvm_type.to_string());
        last_end = fl.offset + fl.size;
    }

    // Tail padding
    if layout.total_size > last_end {
        let pad = layout.total_size - last_end;
        fields.push(format!("[{} x i8]", pad));
    }

    format!("%{} = type {{ {} }}", name, fields.join(", "))
}
