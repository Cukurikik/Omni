import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';

const ROOT_DIR = process.cwd();

// ==========================================
// 👻 OMNI-ORACLE: API GHOST HANDLER GENERATOR
// ==========================================

function runOracleApi() {
    console.log("🔍 [OMNI-ORACLE] Memulai Pemindaian Ghost Endpoint...");

    const tsMapPath = join(ROOT_DIR, 'ui/src/configs/toolsMap.ts');
    const mainGoPath = join(ROOT_DIR, 'api/main.go');
    const mockGoPath = join(ROOT_DIR, 'api/routes/oracle_mocks.go');

    if (!existsSync(tsMapPath) || !existsSync(mainGoPath)) {
        console.error("❌ UI Map atau Main Go tidak ditemukan!");
        return;
    }

    const tsMapCode = readFileSync(tsMapPath, 'utf8');
    const mainGoCode = readFileSync(mainGoPath, 'utf8');

    // 1. Ekstrak semua endpoint dari toolsMap.ts
    // Mencari pola endpoint: '/api/v1/...'
    const endpointRegex = /endpoint:\s*['"\\`]([^'"\\`]+)['"\\`]/g;
    let match;
    const requiredEndpoints = new Set();
    while ((match = endpointRegex.exec(tsMapCode)) !== null) {
        requiredEndpoints.add(match[1]);
    }

    console.log(`📊 Ditemukan ${requiredEndpoints.size} endpoint unik di UI.`);

    // 2. Identifikasi endpoint yang BELUM ada di main.go
    const ghostEndpoints = [];
    requiredEndpoints.forEach(endpoint => {
        // Cek apakah endpoint sudah ada di main.go (mux.HandleFunc atau mux.Handle)
        if (!mainGoCode.includes(`"${endpoint}"`)) {
            ghostEndpoints.push(endpoint);
        }
    });

    if (ghostEndpoints.length === 0) {
        console.log("✅ Semua endpoint UI telah memiliki handler di Backend.");
        return;
    }

    console.log(`⚠️  Ditemukan ${ghostEndpoints.length} Ghost Endpoint! Membangun Handler Mock...`);

    // 3. Generate Mock Handlers di Go
    let mockContent = `package routes\n\n`;
    mockContent += `import (\n\t"encoding/json"\n\t"net/http"\n\t"time"\n)\n\n`;
    mockContent += `// OMNI_ORACLE_MOCK_REGISTRY menyimpan daftar rute otomatis\n`;
    mockContent += `var OracleMockRoutes = map[string]http.HandlerFunc{}\n\n`;
    mockContent += `func init() {\n`;

    ghostEndpoints.forEach(endpoint => {
        const handlerName = "OracleMock_" + endpoint.replace(/[^a-zA-Z0-9]/g, '_');
        
        mockContent += `	OracleMockRoutes["${endpoint}"] = func(w http.ResponseWriter, r *http.Request) {\n`;
        mockContent += `		w.Header().Set("Content-Type", "application/json")\n`;
        mockContent += `		w.WriteHeader(http.StatusOK)\n`;
        mockContent += `		json.NewEncoder(w).Encode(map[string]interface{}{\n`;
        mockContent += `			"status": "mocked",\n`;
        mockContent += `			"message": "Ghost Handler Activated by OMNI-ORACLE",\n`;
        mockContent += `			"endpoint": "${endpoint}",\n`;
        mockContent += `			"timestamp": time.Now().Format(time.RFC3339),\n`;
        mockContent += `		})\n`;
        mockContent += `	}\n`;
    });

    mockContent += `}\n`;

    // Pastikan folder routes ada
    if (!existsSync(join(ROOT_DIR, 'api/routes'))) {
        mkdirSync(join(ROOT_DIR, 'api/routes'), { recursive: true });
    }

    writeFileSync(mockGoPath, mockContent);
    console.log(`✅ [ORACLE SYNC] ${ghostEndpoints.length} Mock Handler berhasil dijahit ke oracle_mocks.go.`);
}

runOracleApi();
