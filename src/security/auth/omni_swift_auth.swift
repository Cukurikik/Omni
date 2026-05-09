import FirebaseAuth
import Foundation

/// Omni Swift Firebase Auth Integration
/// Security & UI Layer
/// Provides secure login, token management, and OIDC bridging for native 
/// iOS clients connecting to the Omni ecosystem.

public class OmniAuthManager {
    public static let shared = OmniAuthManager()
    
    private init() {}
    
    /// Authenticates a user anonymously or via custom token
    public func authenticate(withCustomToken token: String? = nil, completion: @escaping (Result<User, Error>) -> Void) {
        if let customToken = token {
            Auth.auth().signIn(withCustomToken: customToken) { authResult, error in
                if let error = error {
                    completion(.failure(error))
                    return
                }
                guard let user = authResult?.user else {
                    completion(.failure(NSError(domain: "OmniAuth", code: -1, userInfo: [NSLocalizedDescriptionKey: "User object is nil"])))
                    return
                }
                completion(.success(user))
            }
        } else {
            // Fallback to anonymous sign-in for public model access
            Auth.auth().signInAnonymously { authResult, error in
                if let error = error {
                    completion(.failure(error))
                    return
                }
                guard let user = authResult?.user else {
                    completion(.failure(NSError(domain: "OmniAuth", code: -2, userInfo: [NSLocalizedDescriptionKey: "Anonymous User object is nil"])))
                    return
                }
                completion(.success(user))
            }
        }
    }
    
    /// Retrieves the current ID token for making authenticated REST/gRPC calls to Omni nodes
    public func getBearerToken(completion: @escaping (String?) -> Void) {
        guard let currentUser = Auth.auth().currentUser else {
            completion(nil)
            return
        }
        
        currentUser.getIDTokenForcingRefresh(true) { idToken, error in
            if let error = error {
                print("Failed to retrieve ID token: \(error.localizedDescription)")
                completion(nil)
                return
            }
            completion(idToken)
        }
    }
    
    /// Signs out and clears native keychain
    public func signOut() throws {
        try Auth.auth().signOut()
    }
}
