// OMNI Interface — SwiftUI Model Dashboard View
// Native macOS/iOS model monitoring dashboard.

import SwiftUI

struct ModelInfo: Identifiable, Codable {
    let id: String; let name: String; let version: String
    let status: String; let parameters: Int64
    var latencyMs: Double = 0; var throughputRps: Double = 0
    var gpuUtilization: Double = 0
}

struct InferenceMetrics: Codable {
    let totalRequests: Int64; let avgLatencyMs: Double
    let p95LatencyMs: Double; let errorRate: Double
}

@Observable
class DashboardViewModel {
    var models: [ModelInfo] = []
    var metrics = InferenceMetrics(totalRequests: 0, avgLatencyMs: 0, p95LatencyMs: 0, errorRate: 0)
    var isLoading = false; var errorMessage: String?

    func fetchModels() async {
        isLoading = true; defer { isLoading = false }
        guard let url = URL(string: "http://localhost:8080/api/v1/models") else { return }
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            models = try JSONDecoder().decode([ModelInfo].self, from: data)
        } catch { errorMessage = error.localizedDescription }
    }
}

struct OmniDashboardView: View {
    @State private var vm = DashboardViewModel()
    @State private var selectedModel: ModelInfo?

    var body: some View {
        NavigationSplitView {
            VStack(spacing: 0) {
                HStack {
                    Image(systemName: "brain.head.profile")
                        .foregroundStyle(.indigo)
                    Text("OMNI Models").font(.title2.bold())
                    Spacer()
                    Button(action: { Task { await vm.fetchModels() } }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }.padding()

                List(vm.models, selection: $selectedModel) { model in
                    ModelRow(model: model).tag(model)
                }
            }
        } detail: {
            if let model = selectedModel {
                ModelDetailView(model: model)
            } else {
                ContentUnavailableView("Select a Model", systemImage: "cpu",
                    description: Text("Choose a model to view details"))
            }
        }
        .task { await vm.fetchModels() }
    }
}

struct ModelRow: View {
    let model: ModelInfo
    var body: some View {
        HStack {
            Circle()
                .fill(model.status == "production" ? .green : .orange)
                .frame(width: 10, height: 10)
            VStack(alignment: .leading) {
                Text(model.name).font(.headline)
                Text("v\(model.version) • \(model.parameters / 1_000_000)M params")
                    .font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
            Text(String(format: "%.0f ms", model.latencyMs))
                .font(.caption.monospaced())
                .foregroundStyle(model.latencyMs < 100 ? .green : .red)
        }
    }
}

struct ModelDetailView: View {
    let model: ModelInfo
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                HStack {
                    VStack(alignment: .leading) {
                        Text(model.name).font(.largeTitle.bold())
                        Text("Version \(model.version)").foregroundStyle(.secondary)
                    }; Spacer()
                    StatusBadge(status: model.status)
                }.padding()

                LazyVGrid(columns: [GridItem(), GridItem(), GridItem()], spacing: 16) {
                    MetricCard(title: "Latency", value: String(format: "%.1f ms", model.latencyMs), icon: "clock")
                    MetricCard(title: "Throughput", value: String(format: "%.0f rps", model.throughputRps), icon: "bolt")
                    MetricCard(title: "GPU", value: String(format: "%.0f%%", model.gpuUtilization * 100), icon: "cpu")
                }.padding(.horizontal)
            }
        }
    }
}

struct MetricCard: View {
    let title: String; let value: String; let icon: String
    var body: some View {
        VStack(spacing: 8) {
            Image(systemName: icon).font(.title2).foregroundStyle(.indigo)
            Text(value).font(.title.bold())
            Text(title).font(.caption).foregroundStyle(.secondary)
        }
        .frame(maxWidth: .infinity).padding()
        .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 12))
    }
}

struct StatusBadge: View {
    let status: String
    var body: some View {
        Text(status.uppercased()).font(.caption.bold())
            .padding(.horizontal, 8).padding(.vertical, 4)
            .background(status == "production" ? Color.green.opacity(0.2) : Color.orange.opacity(0.2))
            .clipShape(Capsule())
    }
}
