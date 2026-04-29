# OMNI vLLM: Request Router (Continuous Batching)
# Ruby DSL for routing and scheduling incoming generation requests into the PagedAttention engine.
# Source: vllm-project/vllm

module Omni
  module VLLM
    class RoutingError < StandardError; end

    class Request
      attr_reader :id, :prompt, :max_tokens
      attr_accessor :status

      def initialize(id, prompt, max_tokens)
        @id = id
        @prompt = prompt
        @max_tokens = max_tokens
        @status = :queued
      end
    end

    class ContinuousBatcher
      attr_reader :waiting_queue, :running_batch

      def initialize(max_batch_size = 256)
        @max_batch_size = max_batch_size
        @waiting_queue = []
        @running_batch = []
      end

      # Receives a new API request and queues it
      def submit_request(req)
        raise RoutingError, "Invalid request" unless req.is_a?(Request)
        @waiting_queue << req
        req.id
      end

      # Called by the engine scheduling loop every step
      def step_schedule
        # 1. Remove completed requests from the running batch
        @running_batch.reject! { |req| req.status == :completed }

        # 2. Add waiting requests to the running batch up to the batch limit
        available_slots = @max_batch_size - @running_batch.size
        
        if available_slots > 0 && !@waiting_queue.empty?
          to_promote = @waiting_queue.shift(available_slots)
          to_promote.each { |req| req.status = :running }
          @running_batch.concat(to_promote)
        end

        # Return the currently executing batch
        @running_batch
      end

      # Simulated hook for when the engine finishes generating a sequence
      def mark_completed(request_id)
        req = @running_batch.find { |r| r.id == request_id }
        if req
          req.status = :completed
          true
        else
          false
        end
      end
    end
  end
end
