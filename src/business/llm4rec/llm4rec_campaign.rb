# OMNI Business Layer: llm4rec_campaign.rb
# Ruby domain logic for managing LLM4Rec recommendation campaigns.
# Bound: Max 10 active campaigns per tenant to prevent DB lock.

module Omni
  module LLM4Rec
    MAX_CAMPAIGNS_PER_TENANT = 10

    class OmniError < StandardError
      attr_reader :code
      def initialize(code, msg)
        @code = code
        super(msg)
      end
    end

    class OmniResult
      attr_reader :data, :error
      def initialize(data, error = nil)
        @data = data
        @error = error
      end
    end

    class CampaignManager
      def initialize
        @active_campaigns = 0
      end

      def create_campaign(config)
        if @active_campaigns >= MAX_CAMPAIGNS_PER_TENANT
          return OmniResult.new(nil, OmniError.new(1, "Tenant exceeds 10 active campaign bound."))
        end
        
        @active_campaigns += 1
        OmniResult.new({id: "camp_#{Time.now.to_i}", status: "ACTIVE"})
      end
    end
  end
end
