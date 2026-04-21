import SwiftUI

// ==========================================
// 📱 OMNI SWIFTUI: SPATIAL ANIMATIONS
// ==========================================
// Integrasi efek 200 Animasi khusus untuk Mobile Framework Apple (iOS)
// memanfaatkan matchedGeometryEffect dan interaksi spring() fisika dinamis.

struct OMNIDashboardView: View {
    @State private var isAgentActive = false
    @Namespace private var animationSpace

    var body: some View {
        ZStack {
            // Radial Dark Background
            RadialGradient(
                gradient: Gradient(colors: [Color.blue.opacity(0.15), Color.black]),
                center: .top, startRadius: 10, endRadius: 800
            ).edgesIgnoringSafeArea(.all)

            VStack(spacing: 30) {
                // Konsep Animasi Fluid Typography (Morphing)
                Text("OMNI C2 NODE")
                    .font(.system(size: isAgentActive ? 36 : 28, weight: .heavy, design: .rounded))
                    .foregroundColor(.white)
                    .matchedGeometryEffect(id: "title", in: animationSpace)
                    .animation(.spring(response: 0.5, dampingFraction: 0.6), value: isAgentActive)

                // Indikator Swarm Berbasis Skala/Fisika Pegas
                Circle()
                    .fill(isAgentActive ? Color.cyan : Color.gray.opacity(0.3))
                    .frame(width: isAgentActive ? 150 : 80, height: isAgentActive ? 150 : 80)
                    .shadow(color: isAgentActive ? Color.cyan.opacity(0.8) : .clear, radius: 20)
                    .scaleEffect(isAgentActive ? 1.05 : 1)
                    .animation(
                        isAgentActive ? Animation.easeInOut(duration: 1.5).repeatForever(autoreverses: true) : .default,
                        value: isAgentActive
                    )

                Button(action: {
                    withAnimation(.spring(response: 0.4, dampingFraction: 0.5, blendDuration: 0.8)) {
                        self.isAgentActive.toggle()
                    }
                }) {
                    Text(isAgentActive ? "HALT ALL SWARMS" : "ACTIVATE OMNI")
                        .font(.headline)
                        .padding()
                        .frame(width: 250)
                        .background(isAgentActive ? Color.red : Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(16)
                        .shadow(radius: 10)
                }
            }
        }
        .preferredColorScheme(.dark)
    }
}
