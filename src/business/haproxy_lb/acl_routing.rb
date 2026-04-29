module Omni
  module Business
    module HAProxyLB
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

      class ACLRouting
        def evaluate_acl(req_path, req_ip, blocked_ips, admin_cidrs)
          if req_path.nil? || req_ip.nil?
            return OmniResult.new(error: StandardError.new("Path and IP cannot be nil"))
          end

          # Business rules for L7 HAProxy ACLs
          if blocked_ips.include?(req_ip)
            return OmniResult.new(value: { action: "DENY", reason: "IP_BLOCKED" })
          end

          if req_path.start_with?("/admin/")
            unless admin_cidrs.include?(req_ip) # Simplified CIDR check for zero-mock
              return OmniResult.new(value: { action: "DENY", reason: "ADMIN_DENIED" })
            end
            return OmniResult.new(value: { action: "ROUTE_ADMIN_BACKEND", reason: "ADMIN_ALLOWED" })
          end

          if req_path.start_with?("/api/")
            return OmniResult.new(value: { action: "ROUTE_API_BACKEND", reason: "API_MATCH" })
          end

          OmniResult.new(value: { action: "ROUTE_DEFAULT_BACKEND", reason: "DEFAULT_MATCH" })
        end
      end
    end
  end
end
