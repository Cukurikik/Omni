// OmniTermiNetwork.swift — Zero-Dependency Networking
// Inspired by: TermiNetwork
// Layer: Network / Swift
//
// A robust, zero-dependency networking client for iOS/macOS devices to 
// communicate securely with the OMNI backend. Fully implemented.

import Foundation

public enum OmniHTTPMethod: String {
    case get = "GET"
    case post = "POST"
    case put = "PUT"
    case delete = "DELETE"
}

public enum OmniNetworkError: Error {
    case invalidURL
    case noData
    case decodingFailed(Error)
    case unauthorized
    case serverError(statusCode: Int)
}

public protocol OmniEndpoint {
    var path: String { get }
    var method: OmniHTTPMethod { get }
    var headers: [String: String]? { get }
    var body: Data? { get }
}

public class OmniNetworkClient {
    private let baseURL: URL
    private let session: URLSession
    private var authToken: String?

    public init(baseURLString: String, authToken: String? = nil) {
        guard let url = URL(string: baseURLString) else {
            fatalError("Invalid base URL provided to OmniNetworkClient")
        }
        self.baseURL = url
        self.authToken = authToken
        
        let config = URLSessionConfiguration.default
        config.timeoutIntervalForRequest = 30.0
        self.session = URLSession(configuration: config)
    }

    public func setAuthToken(_ token: String) {
        self.authToken = token
    }

    public func request<T: Decodable>(_ endpoint: OmniEndpoint) async throws -> T {
        let url = baseURL.appendingPathComponent(endpoint.path)
        var request = URLRequest(url: url)
        request.httpMethod = endpoint.method.rawValue
        
        if let token = authToken {
            request.addValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        if let headers = endpoint.headers {
            for (key, value) in headers {
                request.addValue(value, forHTTPHeaderField: key)
            }
        }
        
        request.httpBody = endpoint.body

        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw OmniNetworkError.noData
        }
        
        switch httpResponse.statusCode {
        case 200...299:
            do {
                let decoder = JSONDecoder()
                return try decoder.decode(T.self, from: data)
            } catch let error {
                throw OmniNetworkError.decodingFailed(error)
            }
        case 401, 403:
            throw OmniNetworkError.unauthorized
        default:
            throw OmniNetworkError.serverError(statusCode: httpResponse.statusCode)
        }
    }
}
