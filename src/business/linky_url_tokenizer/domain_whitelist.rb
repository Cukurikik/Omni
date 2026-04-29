module Omni
  module Business
    module LinkyUrlTokenizer
      class OmniResult
        attr_reader :value, :error
        
        def initialize(value: nil, error: nil)
          @value = value
          @error = error
        end
        
        def ok?
          @error.nil?
        end
      end

      class DomainWhitelist
        def validate_url_security(url_string)
          if url_string.nil? || url_string.empty?
            return OmniResult.new(error: StandardError.new("URL cannot be empty"))
          end

          # Linky Business Logic: Prevent SSRF (Server-Side Request Forgery)
          # Agents should not be able to crawl local networks or malicious domains
          
          dangerous_patterns = ["localhost", "127.0.0.1", "192.168", "10.0.0", "file://"]
          
          dangerous_patterns.each do |pattern|
            if url_string.include?(pattern)
              return OmniResult.new(value: { 
                secure: false, 
                reason: "SSRF prevention triggered. Local or private networks are blocked." 
              })
            end
          end

          unless url_string.start_with?("https://") || url_string.start_with?("http://")
            return OmniResult.new(value: { secure: false, reason: "Must use HTTP/HTTPS protocol" })
          end

          OmniResult.new(value: { secure: true, reason: "URL safe to tokenize" })
        end
      end
    end
  end
end
