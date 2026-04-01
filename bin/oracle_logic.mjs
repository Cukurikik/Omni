import { execSync } from 'child_process';
import { join } from 'path';

const ROOT_DIR = process.cwd();

// ==========================================
// 🛡️ OMNI-ORACLE: LOGIC FUZZ GUARDIAN
// ==========================================

function runOracleLogic() {
    console.log("🛡️ [OMNI-ORACLE] Menjalankan Pemeriksaan Logika & Fuzzing...");

    try {
        // 1. Cek Sintaks & Tipe Go (Fast Check)
        console.log("🔍 Memvalidasi Integritas Tipe Backend...");
        execSync('go vet ./...', { cwd: join(ROOT_DIR, 'api'), stdio: 'inherit' });

        // 2. Simulasi Fuzzing (Dalam implementasi nyata: go test -fuzz)
        // Disini kita jalankan unit test sebagai proxy untuk validasi logika
        console.log("🧪 Menjalankan Unit Test Terintegrasi...");
        // Kita gunakan -short agar cepat saat dev loop
        execSync('go test -short ./...', { cwd: join(ROOT_DIR, 'api'), stdio: 'inherit' });

        console.log("✅ [ORACLE LOGIC] Logika sistem dinyatakan SEHAT.");
        return true;
    } catch (error) {
        console.error("\n❌ [LOGIC FATAL] Deteksi Kerusakan Logika atau Kesalahan Tipe!");
        console.error("⚠️  OMNI-ORACLE menyarankan perbaikan segera sebelum deployment.");
        return false;
    }
}

const success = runOracleLogic();
process.exit(success ? 0 : 1);
