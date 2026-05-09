# moe_lixaudio_billing.rb — Domain
# Layer: Domain — Lixaudio API Usage Billing
# Inspired by: lixaudio (TTS/STT pipeline router)

module Omni
  module Domain
    class AudioBillingAccount
      attr_reader :account_id, :balance_credits
      
      COST_PER_SECOND = {
        tts: 0.05,
        stt: 0.02,
        sts: 0.08
      }.freeze

      def initialize(account_id, initial_credits = 0.0)
        @account_id = account_id
        @balance_credits = initial_credits
      end

      def add_credits(amount)
        raise ArgumentError, "Amount must be positive" if amount <= 0
        @balance_credits += amount
      end

      # Domain Rule: Pre-flight check before routing audio
      def authorize_stream!(task_type, estimated_seconds)
        rate = COST_PER_SECOND[task_type.to_sym]
        raise ArgumentError, "Invalid audio task type" unless rate
        
        estimated_cost = rate * estimated_seconds
        if @balance_credits < estimated_cost
          raise "Insufficient credits. Required: #{estimated_cost}, Available: #{@balance_credits}"
        end
        true
      end

      def deduct_usage!(task_type, actual_seconds)
        rate = COST_PER_SECOND[task_type.to_sym]
        cost = rate * actual_seconds
        @balance_credits -= cost
        @balance_credits = 0 if @balance_credits < 0 # Prevent negative balance
        cost
      end
    end
  end
end
