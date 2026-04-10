# ============================================================
# OMNI Ruby Bridge — Domain DSL Nexus
# ============================================================
# Layer: Domain (Convention-over-Config, Routing, DSL)
# Menggunakan Ruby Fiddle bawaan — TIDAK perlu `gem install ffi`.
# ============================================================

require 'fiddle'
require 'fiddle/import'

module OmniBridge
  extend Fiddle::Importer

  # Deteksi platform
  LIB_EXT = case RUBY_PLATFORM
            when /mswin|mingw/ then 'omni_core.dll'
            when /darwin/      then 'libomni_core.dylib'
            else                    'libomni_core.so'
            end

  LIB_PATH = File.join(__dir__, '..', '..', 'core', 'target', 'release', LIB_EXT)

  unless File.exist?(LIB_PATH)
    raise LoadError, "[OMNI-E401] Kernel tidak ditemukan: #{LIB_PATH}\nKompilasi: omni build --release"
  end

  dlload LIB_PATH

  # C-ABI function signature
  extern 'void* __omni_ffi(void*, size_t)'

  # Eksekusi fungsi OMNI dari Ruby DSL
  def self.execute(function_name, data_string)
    ptr = Fiddle::Pointer[data_string]
    result_ptr = __omni_ffi(ptr, data_string.bytesize)

    if result_ptr.null?
      raise RuntimeError, "[OMNI-E402] Kernel mengembalikan null pointer"
    end

    result_ptr
  end

  # DSL routing shorthand untuk rb::route
  def self.route(path, &block)
    # Didelegasikan ke OMNI HTTP Router (Phase 12)
    execute("rb_route_register", "#{path}")
    block.call if block_given?
  end
end
