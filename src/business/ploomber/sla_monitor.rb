module Omni
  module Ploomber
    # OMNI Ploomber - SLA Monitor
    # Strict Ruby business logic for tracking DAG execution against SLAs
    
    class SLAMonitor
      attr_reader :max_duration_seconds
      
      def initialize(max_duration_seconds: 3600)
        @max_duration_seconds = max_duration_seconds
      end

      # Monadic return: [Boolean, String/Nil]
      def check_compliance(start_time, end_time)
        return [false, "Start time cannot be after end time"] if start_time > end_time
        
        duration = end_time - start_time
        if duration <= @max_duration_seconds
          [true, nil]
        else
          [false, "SLA Breached: Task took #{duration}s, max allowed is #{@max_duration_seconds}s"]
        end
      end

      def evaluate_batch(task_records)
        breaches = []
        task_records.each do |task|
          compliant, error = check_compliance(task[:start_time], task[:end_time])
          unless compliant
            breaches << { task_id: task[:id], error: error }
          end
        end
        
        if breaches.empty?
          [:ok, "All tasks compliant"]
        else
          [:error, breaches]
        end
      end
    end
  end
end
