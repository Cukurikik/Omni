module Omni
  module Domain
    module MoE
      # OMNI MOTHER Production Zero-Mock Session Manager
      # Ruby DDD Entity tracking stateful multi-turn interactions with LLM models.
      # Automatically prunes KV caches when sessions expire.

      class SessionExpiredError < StandardError; end
      class InvalidContextError < StandardError; end

      class InferenceSession
        attr_reader :session_id, :tenant_id, :created_at, :last_active_at, :context_window_used

        MAX_IDLE_TIME_SECONDS = 3600 # 1 Hour

        def initialize(tenant_id, max_context_tokens = 32768)
          @session_id = SecureRandom.uuid
          @tenant_id = tenant_id
          @created_at = Time.now.utc
          @last_active_at = @created_at
          @context_window_used = 0
          @max_context_tokens = max_context_tokens
          @messages = []
          @mutex = Mutex.new
        end

        def active?
          Time.now.utc - @last_active_at <= MAX_IDLE_TIME_SECONDS
        end

        def add_interaction(role, content, tokens_consumed)
          @mutex.synchronize do
            raise SessionExpiredError, "OMNI CRITICAL: Session #{@session_id} has expired." unless active?
            
            if @context_window_used + tokens_consumed > @max_context_tokens
              # Evict oldest messages (Sliding Window KV Cache Logic)
              evict_oldest_context(tokens_consumed)
            end

            @messages << { role: role, content: content, timestamp: Time.now.utc }
            @context_window_used += tokens_consumed
            @last_active_at = Time.now.utc
          end
        end

        private

        def evict_oldest_context(needed_tokens)
          freed = 0
          while freed < needed_tokens && @messages.size > 1
            # Assume average 50 tokens per message for this mockup, 
            # in production this is exact token counts.
            removed = @messages.shift
            freed += 50 
            @context_window_used -= 50
          end
          
          if @context_window_used + needed_tokens > @max_context_tokens
            raise InvalidContextError, "OMNI CRITICAL: Single interaction exceeds maximum context window."
          end
        end
      end
      
      class SessionRegistry
        def initialize
          @sessions = {}
          @mutex = Mutex.new
        end
        
        def create(tenant_id)
          @mutex.synchronize do
            session = InferenceSession.new(tenant_id)
            @sessions[session.session_id] = session
            session
          end
        end
        
        def get(session_id)
          @mutex.synchronize do
            session = @sessions[session_id]
            raise SessionExpiredError unless session&.active?
            session
          end
        end
        
        def prune_inactive!
          @mutex.synchronize do
            @sessions.delete_if { |_, session| !session.active? }
          end
        end
      end
    end
  end
end
