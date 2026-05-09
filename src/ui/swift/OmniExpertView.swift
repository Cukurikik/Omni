import SwiftUI

// OMNI MOTHER: Swift Expert UI Component

struct OmniExpertView: View {
    let id: String
    let status: String
    
    var body: some View {
        HStack {
            Text(id)
                .fontWeight(.semibold)
            Spacer()
            Text(status)
                .foregroundColor(status == "ONLINE" ? .green : .red)
        }
        .padding()
        .background(Color(UIColor.secondarySystemBackground))
        .cornerRadius(8)
    }
}
