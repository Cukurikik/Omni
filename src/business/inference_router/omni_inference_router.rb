# @omni-layer Business | @omni-lang Ruby | @omni-batch 18 | @omni-semester 16
# @omni-description Ruby transformer inference API router with rate limiting,
# request validation, and model version management.

module Omni
  module Transformer
    class InferenceRouter
      MODELS = {
        'tempo-forecaster' => { version: '1.0.0', type: :timeseries, max_batch: 32 },
        'hiformer-seg'     => { version: '1.0.0', type: :segmentation, max_batch: 8 },
        'video-classifier' => { version: '1.0.0', type: :video, max_batch: 4 },
        'bert-ner'         => { version: '1.0.0', type: :ner, max_batch: 64 },
        'long-text-cls'    => { version: '1.0.0', type: :classification, max_batch: 16 },
      }.freeze

      def initialize(rate_limit: 1000)
        @rate_limit = rate_limit
        @request_counts = Hash.new(0)
        @request_log = []
        @mutex = Mutex.new
      end

      def route(request)
        validate!(request)
        check_rate_limit!(request[:api_key])
        model = MODELS[request[:model_id]]
        raise ModelNotFoundError, request[:model_id] unless model
        log_request(request)
        dispatch(request, model)
      end

      def stats
        @mutex.synchronize do
          { total_requests: @request_log.size, models: MODELS.keys,
            rate_limits: @request_counts.dup }
        end
      end

      private

      def validate!(request)
        raise ValidationError, 'missing model_id' unless request[:model_id]
        raise ValidationError, 'missing api_key' unless request[:api_key]
        raise ValidationError, 'invalid api_key' unless request[:api_key].start_with?('omni_')
      end

      def check_rate_limit!(api_key)
        @mutex.synchronize do
          @request_counts[api_key] += 1
          if @request_counts[api_key] > @rate_limit
            raise RateLimitError, "exceeded #{@rate_limit} requests"
          end
        end
      end

      def dispatch(request, model)
        case model[:type]
        when :timeseries   then forecast(request)
        when :ner          then extract_entities(request)
        when :video        then classify_video(request)
        when :segmentation then segment_image(request)
        else classify_text(request)
        end
      end

      def forecast(req)
        { type: :forecast, model: req[:model_id], horizon: req[:horizon] || 96,
          result: Array.new(req[:horizon] || 96) { |i| Math.sin(i * 0.1) } }
      end

      def extract_entities(req)
        { type: :ner, model: req[:model_id], entities: [], token_count: 0 }
      end

      def classify_video(req)
        { type: :video, model: req[:model_id], label: 'action', confidence: 0.85 }
      end

      def segment_image(req)
        { type: :segmentation, model: req[:model_id], classes: 9 }
      end

      def classify_text(req)
        { type: :classification, model: req[:model_id], label: 'positive', confidence: 0.92 }
      end

      def log_request(request)
        @mutex.synchronize do
          @request_log << { model: request[:model_id], time: Time.now.utc.iso8601 }
          @request_log.shift if @request_log.size > 10_000
        end
      end
    end

    class ModelNotFoundError < StandardError; end
    class ValidationError < StandardError; end
    class RateLimitError < StandardError; end
  end
end
