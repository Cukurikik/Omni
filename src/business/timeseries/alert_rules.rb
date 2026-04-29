module Omni
  module TimeSeries
    class Result
      attr_reader :is_success, :value, :error
      def initialize(is_success, value, error); @is_success = is_success; @value = value; @error = error; end
      def self.success(value); new(true, value, nil); end
      def self.failure(error); new(false, nil, error); end
    end

    class AlertCondition
      attr_reader :metric_name, :operator, :threshold, :duration_seconds

      def initialize(metric_name, operator, threshold, duration_seconds)
        @metric_name = metric_name
        @operator = operator
        @threshold = threshold
        @duration_seconds = duration_seconds
      end

      def evaluate(current_value)
        case @operator
        when :greater_than then current_value > @threshold
        when :less_than then current_value < @threshold
        when :equals then current_value == @threshold
        else false
        end
      end
    end

    class AlertEngine
      def initialize
        @rules = {}
        @state = {} # metric -> { breached_since: Time }
      end

      def add_rule(id, condition)
        @rules[id] = condition
        Result.success(id)
      end

      def process_datapoint(metric_name, value, timestamp = Time.now)
        triggered_alerts = []

        @rules.each do |id, rule|
          next unless rule.metric_name == metric_name

          is_breached = rule.evaluate(value)
          state_key = "#{id}_#{metric_name}"

          if is_breached
            @state[state_key] ||= timestamp
            
            if (timestamp - @state[state_key]) >= rule.duration_seconds
              triggered_alerts << { rule_id: id, metric: metric_name, value: value, time: timestamp }
            end
          else
            @state.delete(state_key)
          end
        end

        Result.success(triggered_alerts)
      end
    end
  end
end
