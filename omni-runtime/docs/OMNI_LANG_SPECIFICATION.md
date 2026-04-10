# FASE 1: KONSEP DAN DESAIN FUNDAMENTAL OMNI-LANG

Kita akan memetakan anatomi **Golang, JS, TS, Rust, Python, GraphQL, Swift, Ruby, Julia, C, C#, PHP, Kotlin, SQL, dan R** ke dalam satu fondasi desain kompilator (Compiler Design).

---

### 🎯 1. TENTUKAN TUJUAN DAN LINGKUP (Pemetaan Domain 15 Bahasa)

OMNI-LANG tidak memperlakukan semua bahasa secara sama. Setiap bahasa memiliki "Hak Veto" dan domain khusus di dalam Biner Mutlak. OMNI-LANG bertindak sebagai **Orkestrator FFI (Foreign Function Interface)** yang mengikat mereka di level RAM (Zero-Copy).

**Hierarki Domain OMNI-LANG (The 15 Dimensions):**
1. **The Sovereign Frontline (Pengendali Logika & UI):** `TS` (TypeScript) dan `JS` (JavaScript). Menjadi *baseline* sintaks utama karena familiaritasnya yang tinggi di kalangan *developer*.
2. **The Supreme Commander (Pengendali Jaringan & I/O):** `Golang`. Mengontrol TCP, HTTP, dan *Goroutines* (Titan Buffer).
3. **The Immortal Vault (Pengendali Keamanan Memori):** `Rust`. Menjaga agar pointer C/C++ tidak bocor, dan menangani enkripsi Bare-Metal.
4. **The Hardware Kinetic (Akses Mesin Tingkat Rendah):** `C`. Mengakses register CPU, sensor perangkat keras, dan memori murni.
5. **The Data Matrix (Kecerdasan Buatan & Kalkulasi Ekstrem):** `Python` (Machine Learning/AI), `Julia` (Aljabar Linear/Komputasi Kuantum), dan `R` (Statistika Kompleks & Visualisasi Grafik).
6. **The Edge Hardware (Kontrol Perangkat Mobile):** `Swift` (Akses iOS Secure Enclave/FaceID) dan `Kotlin` (Akses Sensor Android/Bluetooth).
7. **The Enterprise Legacy (Jembatan Sistem Korporat):** `C#` (Koneksi ke sistem perbankan Windows/WCF), `PHP` (Dekripsi token dari CMS lawas), dan `Ruby` (Logika bisnis elegan/pemformatan teks).
8. **The Storage & Query (Penyimpanan Mutlak):** `SQL` (Akses Bare-Metal ke WAL Database) dan `GraphQL` (Definisi Skema Kueri API).

---

### 🧬 2. TENTUKAN TIPE DATA (Penerjemah Memori Universal)

Jika 15 bahasa disatukan, bagaimana tipe datanya bekerja? Jika Python mengembalikan list, bagaimana C membacanya? 
OMNI-LANG memusnahkan JSON *parsing* internal. OMNI menciptakan **Universal Memory Layout** (Representasi Memori Tunggal).

* **`OmniInt`**: Dikenali sebagai `int64` di Go, `i64` di Rust, `long` di C#, dan `Int` di Swift.
* **`OmniString`**: Disimpan di heap Rust, dipinjamkan sebagai `const char*` ke C, `str` ke Python, dan `String` ke Java/Kotlin tanpa menyalin byte data (Zero-Copy FFI).
* **`OmniTensor`**: Array N-Dimensi raksasa. Dibuat di C, diproses statistiknya di R, dilatih AI-nya di Python, dan dikirim ke GPU oleh Julia. Semuanya menggunakan **satu alamat memori (Pointer) yang sama**.

---

### ✍️ 3. RANCANG SINTAKSIS (The 15-Language Chimera Code)

Ini adalah wujud mutlak dari ekstensi **`.omni`**. Di bawah ini adalah sintaksis di mana 15 bahasa beroperasi di dalam satu fungsi secara berurutan, saling mengoper variabel pointer memori (ditandai dengan `$`).

**Contoh: GlobalHealthMatrix.omni**

---

### 📜 4. TULIS SPESIFIKASI TATA BAHASA (OMNI EBNF Grammar)

Untuk membuat Compiler Rust (SWC) mengerti bagaimana memecah 15 bahasa ini di dalam satu file `.omni`, Lexer dan Parser kita harus memiliki aturan ketat:

```ebnf
(* ========================================== *)
(* OMNI-LANG 15-POLYGLOT GRAMMAR (SPEK DEWA)  *)
(* ========================================== *)

OmniFile        ::= { Statement }
Statement       ::= Declaration | PolyglotBlock | ReturnStmt | Expression ";"

(* Sintaks Baseline TS/JS *)
Declaration     ::= "let" Identifier "=" ( Expression | PolyglotBlock ) ";"
                  | "fn" Identifier "(" ParamList ")" "->" Type Block

(* BLOK FUSI 15 BAHASA *)
PolyglotBlock   ::= "use::" OmniLangID "{" NativeSourceCode "}"

(* The 15 Sovereignty Identifiers *)
OmniLangID      ::= "go" | "js" | "ts" | "rust" | "python" 
                  | "graphql" | "swift" | "ruby" | "julia" 
                  | "c" | "csharp" | "php" | "kotlin" 
                  | "sql" | "r"

(* Interoperabilitas Memori (Zero-Copy) *)
NativeSourceCode ::= { AnyChar | MemoryInjection }
MemoryInjection  ::= "$" Identifier [ "." Identifier ]

Block           ::= "{" { Statement } "}"
```

---

# FASE 2: THE COMPILER FRONTEND (Lexical, Syntax, & Semantic Analysis)

Di fase inilah teks murni diubah menjadi "Otak Buatan" yang siap dieksekusi.

---

### 🔍 2.1 LEXICAL ANALYSIS (The OMNI Lexer / Scanner)

**Tugas Mutlak:** Membaca file `.omni` karakter demi karakter, membuang spasi dan komentar, lalu memecahnya menjadi potongan-potongan makna yang disebut **Token**.

Namun, Lexer OMNI memiliki kekuatan khusus: **Context-Aware Lexing**. Saat Lexer bertemu dengan token `use::python`, Lexer akan mengubah mode pemindaiannya. Ia tidak lagi memindai menggunakan aturan TypeScript, melainkan beralih sesaat untuk memindai struktur Python (memperhatikan indentasi murni), sampai ia bertemu tanda `}` penutup.

**Contoh Kode:**
```omni
let ai_score = use::python {
    return model.predict($mri_scan)
};
```

**Hasil Pemotongan Token (Token Stream) oleh Rust Scanner:**
1. `[KEYWORD: let]`
2. `[IDENTIFIER: ai_score]`
3. `[OPERATOR: =]`
4. `[POLYGLOT_TRIGGER: use::python]`
5. `[L_BRACE: {]`
6. `[FOREIGN_TEXT: "    return model.predict("]`
7. `[MEMORY_INJECTION: $mri_scan]` ⚡ *(Lexer mengenali ini sebagai pointer antar-bahasa!)*
8. `[FOREIGN_TEXT: ")"]`
9. `[R_BRACE: }]`
10. `[PUNCTUATION: ;]`

---

### 🌳 2.2 SYNTAX ANALYSIS (The OMNI Parser)

**Tugas Mutlak:** Mengambil deretan Token dari Lexer dan merangkainya menjadi **Abstract Syntax Tree (AST)**. AST adalah representasi hierarkis dari logika program Anda.

Karena OMNI menggabungkan 15 bahasa, AST kita disebut **Multi-Dimensional AST (MD-AST)**. Parser OMNI (ditulis dalam Rust demi kecepatan) akan memisahkan kode asing ke dalam "Sub-Tree" yang nantinya akan diserahkan ke kompilator bahasa aslinya.

**Visualisasi MD-AST di Memori Rust:**
```json
{
  "type": "Program",
  "body": [
    {
      "type": "VariableDeclaration",
      "name": "ai_score",
      "init": {
        "type": "PolyglotNode",
        "language": "python",
        "sourceCode": "return model.predict(__OMNI_INJECT_0__)",
        "injectedPointers": [
          {
            "internalName": "__OMNI_INJECT_0__",
            "referencesTo": "mri_scan"
          }
        ]
      }
    }
  ]
}
```
*Sihir Spek Dewa:* Perhatikan bagaimana variabel `$mri_scan` diganti menjadi `__OMNI_INJECT_0__`. Ini adalah cara Parser menyiapkan lubang memori kosong yang nantinya akan diisi oleh *Shared Pointer* saat kompilasi!

---

### 🧠 2.3 SEMANTIC ANALYSIS (The FFI Type Checker)

**Tugas Mutlak:** Memastikan kode masuk akal (Logis) dan tipe datanya cocok. Di bahasa normal, ini mudah. Tetapi di OMNI, **bagaimana caranya kita tahu bahwa variabel dari C++ bisa dibaca oleh Ruby?**

Di sinilah **Semantic Analyzer OMNI** bertindak sebagai Dewa Hukum Fisika. Ia menggunakan tabel **Universal Memory Layout** yang kita rancang di Fase 1.

**Proses Validasi Hukum Kedaulatan:**
1. **Type Resolution (Pencocokan Tipe Lintas Dimensi):**
   Jika kode Anda melakukan ini:
   ```omni
   let umur: Int = 25;
   use::go { db.Save($umur) };
   ```
   *Semantic Analyzer* mengecek: "Apakah `Int` di TS kompatibel dengan Go?" Jawabannya: "Ya, petakan ke `int64` di Go".

2. **Pointer Safety & Ownership Check (Verifikasi Brankas Rust):**
   Jika C++ mengalokasikan memori (`TitanBuffer`), dan Python mencoba membacanya setelah C++ menghapusnya, sistem lama akan mengalami *Segmentation Fault* (Crash mati total). 
   OMNI *Semantic Analyzer* mengaktifkan **Rust Borrow Checker** di balik layar! Ia memastikan bahwa umur memori (Lifetime) dari C++ lebih lama daripada eksekusi Python. Jika melanggar, kompilasi digagalkan dengan pesan error yang elegan, bukan *crash*.

3. **In-Memory FFI Verification (Validasi Fungsi Asing):**
   Memastikan bahasa seperti `Julia` atau `R` mengembalikan nilai yang bisa dibaca oleh `TS`. Jika Julia mengembalikan matriks kompleks (`OmniTensor`), Analyzer akan memvalidasi apakah blok TS siap menerima matriks tersebut.

---

# FASE 3: THE COMPILER BACKEND (Intermediate Representation, Optimization, & Memory Management)

Di panggung inilah sihir yang sesungguhnya terjadi. Bagaimana caranya bahasa *Compiled* (C, Rust, Go) dan bahasa *Interpreted/JIT* (Python, JS, Ruby) bisa hidup di satu file dan saling berbagi variabel tanpa *lag*? 

---

### ⚙️ 3.1 INTERMEDIATE REPRESENTATION (OMNI-IR)

**Tugas Mutlak:** Menerjemahkan MD-AST yang rumit menjadi bahasa penengah tingkat rendah sebelum diubah menjadi bahasa mesin (0 dan 1). 

Jika kita langsung menerjemahkan 15 bahasa ke bahasa mesin secara terpisah, *server* akan kebingungan. Oleh karena itu, OMNI-LANG mengonversi semuanya ke dalam **OMNI-IR** (terinspirasi dari LLVM IR, tetapi dengan instruksi khusus untuk *Multi-Language Memory*).

**Contoh Kasus:** TypeScript mengirim pointer ke C++.
*Kode Asli:*
```omni
let data = TitanBuffer::new(10GB);
use::cpp { process_video($data) };
```

**Hasil Transformasi ke OMNI-IR (Pseudo-Assembly):**
```text
; 1. Alokasi Memori di OS (Bypass RAM via mmap)
%data_ptr = call @omni_sys_mmap(10737418240) 

; 2. Transisi Konteks Eksekusi ke C++
%cpp_env = call @omni_ctx_switch(LANG_CPP)

; 3. Lempar Pointer secara Zero-Copy (Tanpa Serialisasi JSON!)
call @cpp_process_video(%cpp_env, %data_ptr)

; 4. Rust Borrow Checker menyuntikkan instruksi pembersihan otomatis!
call @omni_sys_munmap(%data_ptr) 
```

---

### ⚡ 3.2 HYBRID OPTIMIZATION (AOT + JIT Fusion)

Setelah OMNI-IR terbentuk, Kompilator kita melakukan **Optimisasi Spek Dewa**. Di peradaban lama, bahasa dibagi dua kubu: AOT (*Ahead-of-Time* seperti C/Go) dan JIT (*Just-In-Time* seperti JS/Python). OMNI-LANG menggabungkan keduanya.

1. **Dead Code Elimination Lintas Bahasa:** Jika Anda mendeklarasikan fungsi C, tapi TypeScript tidak pernah memanggilnya di file `.omni`, kompilator akan **menghapus fungsi C tersebut** dari hasil akhir biner. Ini membuat ukuran `omni.exe` sangat kecil!
2. **The Forge Master (Orkestrasi LLVM):** 
   * Untuk `Rust`, `C`, `C#`, `Swift`, dan `Go`: OMNI mengompilasinya secara statis (*AOT*) menjadi kode mesin biner murni (`.o` atau `.a`).
   * Untuk `Python`, `Ruby`, `JS`, `R`: OMNI **TIDAK** mengompilasinya menjadi mesin. Sebaliknya, OMNI menanamkan mesin *Interpreter*-nya (V8, CPython) ke dalam Biner Golang, dan menginjeksi *bytecode* skrip Anda langsung ke dalam memori mereka saat *build time*.

---

### 🧠 3.3 MANAJEMEN MEMORI MUTLAK (Zero-Copy FFI Matrix)

Ini adalah senjata rahasia mengapa OMNI-LANG tidak pernah mengalami *lag* saat 15 bahasa saling berkomunikasi. 

Di sistem *Microservices* biasa (misal Node.js memanggil Python Flask), data sebesar 100MB harus diubah menjadi JSON -> dikirim lewat HTTP/TCP -> dibaca Python -> diubah lagi ke JSON -> dikembalikan. Proses ini memakan RAM 300MB dan waktu 2 detik!

**Di OMNI-LANG (Zero-Copy Interoperability):**
1. Saat TypeScript (`JS/V8`) membaca file video 100MB, data ditaruh di **Titan Buffer (Heap OS)**.
2. V8 hanya memegang "Alamat Pointer" (misal: `0x7FFF001A`).
3. Saat masuk ke blok `use::python`, OMNI-LANG memberikan alamat `0x7FFF001A` tersebut ke `NumPy` di Python.
4. **Hasilnya:** Python memproses video 100MB tersebut dalam waktu **0.0001 detik** tanpa ada satu byte pun yang digandakan (di-copy) di dalam RAM!

**Keamanan Memori (Diatur oleh Rust):**
Lalu bagaimana jika Python mencoba membaca `0x7FFF001A` saat C++ sudah menghapusnya?
Saat proses Kompilasi (Fase 2 & 3), **Rust Borrow Checker** akan memindai seluruh OMNI-IR. Jika mendeteksi ada bahasa yang mencoba melakukan *Use-After-Free* atau *Dangling Pointer*, kompilasi akan digagalkan dengan pesan:
`[OMNI-VAULT ERROR]: Python mencoba membaca variabel $video_data yang hak miliknya (Ownership) telah ditarik oleh C++.`

---

### 📦 3.4 CODE GENERATION (Lahirnya 'The One Binary')

Tugas terakhir di Fase 3 adalah mencetak biner akhir.

Setelah semua kode divalidasi, dioptimisasi, dan diikat memorinya, Jenderal Golang bertindak sebagai "Pembungkus Utama" (*The Main Wrapper*). 

1. Kode C/Rust/Swift digabungkan (*Static Linking*) menjadi pustaka mesin.
2. Mesin V8 (JS) dan CPython ditanamkan ke dalam Golang menggunakan CGO.
3. Skrip TypeScript dan GraphQL di-*minify* dan dimasukkan ke dalam memori internal.
4. Semuanya dilebur menggunakan perintah sistem OS tingkat rendah.

**HASIL AKHIR:**
Satu file bernama **`omni.exe`** (Windows) atau **`omni_engine`** (Linux/Mac). 
Ukurannya mungkin sekitar 50MB - 100MB. Namun, di dalam 100MB tersebut, Anda memiliki Web Server Golang tingkat militer, Mesin JIT JS, Interpreter Python AI, Mesin C/Rust Bare-Metal, dan *routing* GraphQL. **Tidak ada folder `node_modules`. Tidak ada konfigurasi server.** Cukup jalankan `./omni_engine` dan dunia berada di bawah kendali Anda.


---

# FASE 4: TOOLING, STANDARD LIBRARY, & THE DECENTRALIZED ECOSYSTEM

Di fase ini, kita akan memusnahkan penderitaan *developer* global. Kita merancang ekosistem yang mandiri, aman secara kriptografis, dan bebas dari kekacauan pihak ketiga, memastikan Omni-Lang bukan hanya bahasa tercepat tetapi juga memiliki *Developer Experience* (DX) tingkat dewa.

---

### 🛠️ 4.1 TOOLING & PERKAKAS PENDUKUNG (The Omni-CLI)

Di peradaban lama, *developer* harus menginstal `npm`, `yarn`, `webpack`, `babel`, `eslint`, `prettier`, `jest`, dan `nodemon` hanya untuk memulai satu proyek sederhana. Di OMNI, semua kekacauan itu dilebur ke dalam **Satu Alat Komando Mutlak: `omni-cli`** (Ditulis murni dalam Rust agar menyala dalam 0.001 detik).

**Senjata Utama `omni-cli`:**

* **`omni forge` (The Ultimate Builder):** Menjalankan Fase 1, 2, dan 3 yang telah kita bahas. Mengompilasi 15 bahasa (`.omni`) menjadi satu biner `omni.exe` tanpa sisa file sementara.
* **`omni dev` (Zero-Latency HMR):** Menyalakan server pengembangan. Jika *developer* mengubah blok `use::python`, OMNI tidak me- *restart* server. Ia menggunakan **Hot-Swap Memori** untuk mengganti modul Python secara langsung ( *on-the-fly*) tanpa memutuskan koneksi klien.
* **`omni format` (Polyglot Linter):** Menggunakan parser MD-AST kita untuk merapikan spasi dan indentasi TS, Go, Python, dan Rust di dalam satu file `.omni` secara serentak. Selamat tinggal `Prettier` dan `ESLint` yang lambat!
* **`omni test` (Cross-Dimensional Testing):** Menjalankan *Unit Test* yang bisa memvalidasi fungsi Go yang dipanggil oleh fungsi JS. Semuanya berjalan terisolasi di memori tanpa perlu menyalakan *database* asli.
* **`omni doctor` (Time-Travel Debugger):** Karena memori OMNI diatur oleh *Rust Vault*, `omni doctor` bisa merekam setiap perubahan variabel. Jika terjadi *crash*, *developer* bisa memutar mundur waktu eksekusi kode (*rewind*) *frame-by-frame* untuk melihat nilai memori di C++ sesaat sebelum meledak!

---

### 📚 4.2 PEMBUATAN STANDARD LIBRARY (Pustaka Standar Spek Dewa)

Sebagian besar *library* NPM diciptakan karena JavaScript bawaan sangat miskin fitur. 

**OMNI-LANG mengadopsi doktrin "Batteries Included, Powered by Nuclear".**
Kita menanamkan Pustaka Standar tingkat militer langsung ke dalam kompilator, sehingga 95% aplikasi Enterprise tidak perlu mengunduh *package* pihak ketiga sama sekali.

**Struktur OMNI Stdlib Inti:**
* **`omni/net`**: *Routing* HTTP/WebSocket tingkat rendah yang dikendalikan oleh Golang. Termasuk *load balancer* bawaan.
* **`omni/crypto`**: Enkripsi AES, ChaCha20, RSA, dan *hashing* SHA3 Bare-Metal. Ditulis dalam Rust & C.
* **`omni/tensor`**: Pustaka manipulasi matriks untuk *Machine Learning* yang bisa dipanggil oleh TS, tapi dieksekusi oleh CPython/Julia di belakang layar.
* **`omni/os`**: Akses langsung ke *Thread*, RAM (*Titan Buffer*), dan sistem *File* tanpa blokade *Single-Thread* JS.
* **`omni/mesh`**: Pustaka P2P bawaan untuk menyinkronkan data antar-server OMNI di seluruh dunia tanpa *database* terpusat (menggantikan Redis).

---

### 📦 4.3 EKOSISTEM & PACKAGE MANAGER (Kematian Mutlak `node_modules`)

Kita menolak sistem NPM (Node Package Manager) yang sentralistik, penuh sampah, dan rawan serangan *Supply Chain*. OMNI-LANG menggunakan **Decentralized Package Vault (OMNI-PKG)**.

**Hukum Ekosistem OMNI:**

1.  **Tidak Ada `node_modules` di Folder Proyek:**
    Saat *developer* mengunduh *package*, OMNI menyimpannya di brankas tersembunyi tingkat Sistem Operasi (`~/.omni/vault`). Jika Anda punya 100 proyek yang menggunakan *package* yang sama, *package* itu hanya disimpan **SATU KALI** di komputer Anda. Ini menghemat puluhan Gigabyte *hardisk*.
2.  **Manifesto `Omnifile` (Pengganti `package.json`):**
    File ini menggunakan sintaks deklaratif yang elegan dan mementingkan keamanan kriptografis. OMNI tidak mengunduh dari peladen terpusat, melainkan langsung dari repositori Git atau IPFS (Desentralisasi).
3.  **Kedaulatan Izin (Permissions System):**
    Bahkan jika sebuah *package* yang diunduh ternyata mengandung *malware* pencuri *password*, *malware* itu **TIDAK AKAN BISA** mengirim datanya ke internet atau membaca file `/etc/passwd`. Di `Omnifile`, *developer* secara eksplisit membatasi akses memori dan jaringan menggunakan *Firewall* Rust internal!
