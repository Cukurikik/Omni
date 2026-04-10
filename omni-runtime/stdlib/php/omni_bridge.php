<?php
// ============================================================
// OMNI PHP Bridge — Legacy Web API Nexus
// ============================================================
// Layer: API/Legacy (Request lifecycle, CMS, Laravel bridge)
// Menggunakan PHP FFI bawaan (PHP 7.4+) — TIDAK perlu composer.
// ============================================================

final class OmniBridge
{
    private FFI $ffi;
    private static ?self $instance = null;

    private function __construct()
    {
        $libExt = PHP_OS_FAMILY === 'Windows' ? 'omni_core.dll' : 'libomni_core.so';
        $libPath = __DIR__ . '/../../core/target/release/' . $libExt;

        if (!file_exists($libPath)) {
            throw new RuntimeException(
                "[OMNI-E501] Kernel tidak ditemukan: {$libPath}\n" .
                "Kompilasi dengan: omni build --release"
            );
        }

        $this->ffi = FFI::cdef("
            void* __omni_ffi(void* args_buffer, size_t len);
        ", $libPath);
    }

    public static function getInstance(): self
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    /**
     * Eksekusi fungsi OMNI melalui C-ABI.
     *
     * @param string $functionName Nama fungsi di registry OMNI
     * @param string $data Data mentah (binary safe)
     * @return FFI\CData Pointer ke result buffer
     */
    public function execute(string $functionName, string $data): FFI\CData
    {
        $len = strlen($data);
        $cdata = $this->ffi->new("uint8_t[$len]");
        FFI::memcpy($cdata, $data, $len);

        /** @phpstan-ignore-next-line Dynamic method from FFI::cdef */
        $result = $this->ffi->__omni_ffi(\FFI::addr($cdata), $len);

        if (FFI::isNull($result)) {
            throw new RuntimeException("[OMNI-E502] Kernel mengembalikan null pointer");
        }

        return $result;
    }
}
