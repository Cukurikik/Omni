# SKILL: INTERFACE LAYER — TypeScript, HTML, Swift
**File:** `languages/SKILL_layer_interface.md`  
**Layer:** Languages  
**Bahasa:** TypeScript · HTML · Swift

---

## Peran Domain

Interface Layer menangani semua yang dilihat dan disentuh pengguna. Layer ini HANYA berisi rendering logic — tidak ada business logic, tidak ada akses memori langsung.

| Bahasa | Keunggulan | Kapan Digunakan |
|--------|-----------|-----------------|
| **TypeScript** | Static typing, full-stack safety, React/Vue/Angular | Web app, dashboard, API client |
| **HTML** | Declarative layout, semantic structure, WASM host | Struktur halaman, template email, dokumen |
| **Swift** | Native iOS/macOS, spatial computing, SwiftUI | Mobile app, Apple Watch, Vision Pro |

---

## TypeScript — Idiom OMNI

```omni
// Komponen dashboard dengan strong typing
ts:: type DataPoint = {
  timestamp: number
  value: number
  label: string
}

ts:: type ChartProps = {
  data: DataPoint[]
  title: string
  refreshInterval?: number
}

@html_template("chart")
component SalesChart(props: ts::ChartProps) -> ts::JSX {
  // Hanya rendering logic — data sudah diproses di domain layer
  return (
    <div class="chart-container">
      <h2>{props.title}</h2>
      <canvas id="chart" data-points={JSON.stringify(props.data)} />
    </div>
  )
}

// API client dengan type safety
ts:: async fn fetch_sales_data(period: "daily" | "weekly" | "monthly")
  -> Result<ts::DataPoint[], ApiError> {
  let response = await ts::fetch("/api/sales?period=" + period)
  if !response.ok {
    return Err(ApiError::HttpError(response.status))
  }
  Ok(await response.json::<ts::DataPoint[]>())
}
```

---

## HTML — Idiom OMNI

```omni
// Template deklaratif — tidak ada logic di sini
@html_template("invoice")
template InvoiceDocument(data: InvoiceData) {
  <!DOCTYPE html>
  <html lang="id">
  <head>
    <meta charset="UTF-8">
    <title>Invoice #{data.invoice_number}</title>
  </head>
  <body>
    <header class="invoice-header">
      <img src="{data.company_logo}" alt="{data.company_name}" />
      <h1>INVOICE</h1>
    </header>
    <main>
      <omni:for item in data.line_items>
        <div class="line-item">
          <span>{item.description}</span>
          <span>{item.amount | format_currency}</span>
        </div>
      </omni:for>
    </main>
  </body>
  </html>
}
```

---

## Swift — Idiom OMNI (iOS/macOS)

```omni
// SwiftUI view dengan OMNI data binding
swift:: struct DashboardView: View {
  @StateObject var viewModel: DashboardViewModel
  @State var selectedPeriod: String = "daily"

  var body: some View {
    NavigationView {
      VStack {
        Picker("Period", selection: $selectedPeriod) {
          Text("Daily").tag("daily")
          Text("Weekly").tag("weekly")
          Text("Monthly").tag("monthly")
        }
        .pickerStyle(.segmented)

        if viewModel.isLoading {
          ProgressView()
        } else {
          ChartView(data: viewModel.salesData)
        }
      }
      .navigationTitle("Sales Dashboard")
      .onAppear { viewModel.loadData(period: selectedPeriod) }
    }
  }
}
```

---

## WASM Integration

```omni
// Kompilasi compute module ke WebAssembly untuk dijalankan di browser
@wasm_export
fn compute_in_browser(data: *const f64, len: usize) -> f64 {
  let slice = unsafe { rust::slice::from_raw_parts(data, len) }
  julia::compute_stats(slice)
}

// Di TypeScript, panggil WASM module
ts:: const wasm = await WebAssembly.instantiateStreaming(fetch("/app.wasm"))
ts:: const result = wasm.instance.exports.compute_in_browser(dataPtr, dataLen)
```

---

## Aturan Interface Layer

1. DILARANG ada kalkulasi bisnis di komponen — semua data harus sudah siap saji dari domain layer
2. DILARANG import dari system layer — UI tidak boleh menyentuh pointer atau memori
3. Semua komponen HARUS stateless by default — gunakan state management yang terisolasi
4. TypeScript HARUS strict mode — `"strict": true` di tsconfig.json, tidak ada `any`

---

*ANTIGRAVITY Skills — languages/SKILL_layer_interface.md*
