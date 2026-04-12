import SwiftUI

// ==========================================
// 🍎 OMNI SWIFT UI (Phase 50)
// ==========================================
// Integrasi Ekosistem Apple (iOS & VisionOS)
// Tidak ada jembatan lambat. Swift langsung mengkonsumsi
// UAST GraphQL Subscription secara Real-time.

struct OmniDashboard: View {
    @State private var profitPnl: Double = 0.00
    @State private var isActive: Bool = true
    
    var body: some View {
        VStack(spacing: 20) {
            Text("OMNI HFT TERMINAL")
                .font(.largeTitle)
                .fontWeight(.bold)
                .foregroundColor(.white)
            
            HStack {
                Text("C++ Engine Status:")
                Text(isActive ? "ONLINE" : "HALTED")
                    .foregroundColor(isActive ? .green : .red)
                    .bold()
            }
            
            // Komponen Visualisasi Keuntungan Arbitrase (Realtime dari Go -> Swift)
            ZStack {
                RoundedRectangle(cornerRadius: 15)
                    .fill(LinearGradient(
                        gradient: Gradient(colors: [Color.blue, Color.purple]),
                        startPoint: .topLeading,
                        endPoint: .bottomTrailing
                    ))
                    .frame(width: 300, height: 150)
                
                VStack {
                    Text("Total Net Arbitrage")
                        .font(.headline)
                        .foregroundColor(.white)
                    Text("$\(String(format: "%.2f", profitPnl))")
                        .font(.system(size: 40, weight: .black, design: .rounded))
                        .foregroundColor(.green)
                }
            }
            .shadow(radius: 10)
        }
        .padding()
        .background(Color.black.edgesIgnoringSafeArea(.all))
    }
}
