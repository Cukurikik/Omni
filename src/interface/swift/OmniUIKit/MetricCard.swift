import Foundation

// OMNI MOTHER: iOS Native Metric Card (Production Grade)
// Reusable SwiftUI component.

struct MetricCard {
    let title: String
    let value: String
    
    var body: String {
        return """
        HStack {
            Text("\(title)")
                .foregroundColor(.gray)
            Spacer()
            Text("\(value)")
                .bold()
                .foregroundColor(.moePink)
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .shadow(radius: 5)
        """
    }
}
