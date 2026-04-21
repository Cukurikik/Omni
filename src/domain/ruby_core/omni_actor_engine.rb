# ===========================================================================
# OMNI ACTOR ENGINE (SEMESTER 3 — BATCH 38.5)
# ===========================================================================
# Absorbed From  : Celluloid + concurrent-ruby Actor + Ractor concepts
# Logic Inherited: Ruby / Business Layer (Actor Model Concurrency)
# ===========================================================================
#
# By studying Celluloid, Mother learned Ruby actor patterns:
#   1. Each actor has its own mailbox (message queue)
#   2. Messages are processed one at a time (no shared state)
#   3. Actors communicate exclusively via message passing
#   4. Supervisor restarts crashed actors automatically
#   5. Actor hierarchy enables fault-tolerant systems

# frozen_string_literal: true

require 'thread'

module Omni
  module Actor
    # ================================================================
    # Actor Base Class
    # ================================================================

    class Base
      attr_reader :name, :state, :mailbox_size

      def initialize(name)
        @name = name
        @mailbox = Queue.new
        @state = :idle
        @running = false
        @thread = nil
        @handlers = {}
        @total_messages = 0
        @total_errors = 0
        @total_processed = 0
        @mutex = Mutex.new
        @supervisor = nil

        register_default_handlers
      end

      # Register a message handler
      def on(message_type, &block)
        @handlers[message_type] = block
        self
      end

      # Send a message to this actor (async, non-blocking)
      def tell(message_type, payload = nil)
        @mailbox << { type: message_type, payload: payload, timestamp: Time.now }
        @total_messages += 1
        self
      end

      # Alias for tell
      alias_method :<<, :tell

      # Send a message and wait for response (sync, blocking)
      def ask(message_type, payload = nil, timeout: 5)
        response_queue = Queue.new
        @mailbox << {
          type: message_type,
          payload: payload,
          timestamp: Time.now,
          reply_to: response_queue
        }
        @total_messages += 1

        begin
          Timeout.timeout(timeout) { response_queue.pop }
        rescue Timeout::Error
          { error: :timeout, message: "Ask timed out after #{timeout}s" }
        end
      end

      # Start the actor's processing loop
      def start
        return if @running

        @running = true
        @state = :running
        @thread = Thread.new { process_loop }
        self
      end

      # Stop the actor gracefully
      def stop
        @running = false
        @mailbox << { type: :_stop, payload: nil, timestamp: Time.now }
        @thread&.join(5)
        @state = :stopped
        self
      end

      # Current mailbox depth
      def pending_messages
        @mailbox.size
      end

      def alive?
        @running && @thread&.alive?
      end

      def diagnostics
        {
          name: @name,
          state: @state,
          alive: alive?,
          pending_messages: pending_messages,
          total_messages: @total_messages,
          total_processed: @total_processed,
          total_errors: @total_errors,
          handlers: @handlers.keys
        }
      end

      private

      def register_default_handlers
        on(:_stop) { @running = false }
        on(:ping) { |_msg, reply| reply&.push(:pong) }
        on(:status) { |_msg, reply| reply&.push(diagnostics) }
      end

      def process_loop
        while @running
          begin
            msg = @mailbox.pop
            break unless @running || msg[:type] == :_stop

            handler = @handlers[msg[:type]]
            if handler
              @state = :processing
              result = handler.call(msg[:payload], msg[:reply_to])
              msg[:reply_to]&.push(result) unless msg[:type] == :_stop
              @total_processed += 1
            else
              msg[:reply_to]&.push({ error: :unknown_message, type: msg[:type] })
            end

            @state = :idle
          rescue StandardError => e
            @total_errors += 1
            @state = :error

            # Notify supervisor if available
            @supervisor&.handle_failure(self, e)

            @state = :idle
          end
        end
      rescue StandardError => e
        @state = :crashed
        @supervisor&.handle_crash(self, e)
      end
    end

    # ================================================================
    # Supervisor (restarts crashed actors)
    # ================================================================

    class Supervisor
      STRATEGIES = {
        one_for_one: :restart_one,      # Restart only the failed actor
        one_for_all: :restart_all,      # Restart all children
        rest_for_one: :restart_rest     # Restart failed + those started after
      }.freeze

      attr_reader :children, :strategy

      def initialize(strategy: :one_for_one, max_restarts: 5, restart_window: 60)
        @strategy = strategy
        @children = []
        @max_restarts = max_restarts
        @restart_window = restart_window
        @restart_log = []
        @mutex = Mutex.new
        @total_restarts = 0
      end

      # Add a child actor under supervision
      def supervise(actor)
        @mutex.synchronize do
          actor.instance_variable_set(:@supervisor, self)
          @children << { actor: actor, factory: -> { clone_actor(actor) } }
        end
        actor.start
        self
      end

      # Handle actor failure (non-crash error)
      def handle_failure(actor, error)
        log_event(:failure, actor.name, error.message)
      end

      # Handle actor crash (unrecoverable error)
      def handle_crash(actor, error)
        log_event(:crash, actor.name, error.message)

        return if exceeded_restart_limit?

        @mutex.synchronize do
          case @strategy
          when :one_for_one
            restart_actor(actor)
          when :one_for_all
            restart_all_actors
          when :rest_for_one
            restart_from(actor)
          end
        end
      end

      # Stop all children
      def shutdown
        @mutex.synchronize do
          @children.each { |child| child[:actor].stop }
        end
      end

      def diagnostics
        {
          engine: 'OmniActorEngine::Supervisor',
          strategy: @strategy,
          total_children: @children.size,
          total_restarts: @total_restarts,
          restart_log_size: @restart_log.size,
          children: @children.map { |c| c[:actor].diagnostics }
        }
      end

      private

      def restart_actor(actor)
        idx = @children.index { |c| c[:actor].name == actor.name }
        return unless idx

        old = @children[idx][:actor]
        old.stop rescue nil

        new_actor = old.class.new(old.name)
        # Re-register handlers would need factory pattern
        new_actor.start
        @children[idx][:actor] = new_actor
        @total_restarts += 1
      end

      def restart_all_actors
        @children.each { |child| restart_actor(child[:actor]) }
      end

      def restart_from(actor)
        idx = @children.index { |c| c[:actor].name == actor.name }
        return unless idx

        @children[idx..].each { |child| restart_actor(child[:actor]) }
      end

      def clone_actor(actor)
        actor.class.new(actor.name)
      end

      def exceeded_restart_limit?
        now = Time.now
        @restart_log.reject! { |t| now - t > @restart_window }
        @restart_log.size >= @max_restarts
      end

      def log_event(type, actor_name, message)
        @restart_log << Time.now
      end
    end

    # ================================================================
    # Actor System (Registry + Lookup)
    # ================================================================

    class System
      def initialize
        @actors = {}
        @supervisors = []
        @mutex = Mutex.new
      end

      def spawn(name, actor_class = Base, &setup)
        actor = actor_class.new(name.to_s)
        setup&.call(actor)
        @mutex.synchronize { @actors[name.to_s] = actor }
        actor.start
        actor
      end

      def lookup(name)
        @mutex.synchronize { @actors[name.to_s] }
      end

      def create_supervisor(**opts)
        sup = Supervisor.new(**opts)
        @supervisors << sup
        sup
      end

      def shutdown
        @supervisors.each(&:shutdown)
        @actors.values.each(&:stop)
      end

      def diagnostics
        {
          engine: 'OmniActorEngine',
          layer: 'Ruby Business',
          total_actors: @actors.size,
          total_supervisors: @supervisors.size,
          actors: @actors.transform_values(&:diagnostics),
          learned_logic: [
            'celluloid-actor-model',
            'mailbox-queue-per-actor',
            'tell-async-fire-forget',
            'ask-sync-blocking-reply',
            'supervisor-one-for-one',
            'supervisor-one-for-all',
            'max-restart-rate-limit',
            'actor-registry-lookup'
          ]
        }
      end
    end
  end
end
