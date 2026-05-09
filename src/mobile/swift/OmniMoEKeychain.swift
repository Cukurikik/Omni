// OMNI Framework - MoE Keychain Manager (Swift)
// Securely stores the Tenant API Key in the iOS Secure Enclave Keychain 
// so it is not exposed in UserDefaults.

import Foundation
import Security

class OmniMoEKeychain {
    static let service = "com.omniframework.moe"
    
    static func saveKey(_ key: String, account: String = "tenant_api_key") -> Bool {
        guard let data = key.data(using: .utf8) else { return false }
        
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecValueData as String: data
        ]
        
        SecItemDelete(query as CFDictionary)
        let status = SecItemAdd(query as CFDictionary, nil)
        
        print("OMNI Swift: API Key saved to Secure Enclave.")
        return status == errSecSuccess
    }
    
    static func getKey(account: String = "tenant_api_key") -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrService as String: service,
            kSecAttrAccount as String: account,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        
        var dataTypeRef: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &dataTypeRef)
        
        if status == errSecSuccess, let data = dataTypeRef as? Data {
            return String(data: data, encoding: .utf8)
        }
        return nil
    }
}
