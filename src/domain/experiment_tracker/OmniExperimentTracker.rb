// OmniExperimentTracker.rb — Experiment Tracking DSL
// Inspired by: MLflow/W&B experiment management
// Layer: Domain / Ruby
//
// Convention-over-configuration experiment tracker with
// automatic metric logging, parameter diff, and run comparison.

module Omni
  module Domain
    class ExperimentRun
      attr_reader :run_id, :experiment_name, :status, :start_time,
                  :end_time, :params, :metrics, :artifacts, :tags

      VALID_STATUSES = %w[running completed failed cancelled].freeze

      def initialize(experiment_name:, params: {}, tags: {})
        @run_id = generate_run_id
        @experiment_name = experiment_name
        @status = "running"
        @start_time = Time.now.utc
        @end_time = nil
        @params = params.dup.freeze
        @metrics = Hash.new { |h, k| h[k] = [] }
        @artifacts = []
        @tags = tags.dup
      end

      def log_metric(name, value, step: nil)
        raise "Run is not active" unless @status == "running"

        step ||= @metrics[name].length
        @metrics[name] << {
          value: value.to_f,
          step: step,
          timestamp: Time.now.utc
        }
      end

      def log_metrics(hash, step: nil)
        hash.each { |name, value| log_metric(name, value, step: step) }
      end

      def log_artifact(path, description: "")
        raise "Run is not active" unless @status == "running"

        @artifacts << {
          path: path,
          description: description,
          logged_at: Time.now.utc,
          size_bytes: File.exist?(path) ? File.size(path) : 0
        }
      end

      def complete!
        @status = "completed"
        @end_time = Time.now.utc
      end

      def fail!(error_message = nil)
        @status = "failed"
        @end_time = Time.now.utc
        @tags["error"] = error_message if error_message
      end

      def cancel!
        @status = "cancelled"
        @end_time = Time.now.utc
      end

      def duration_seconds
        return nil unless @end_time
        (@end_time - @start_time).round(2)
      end

      def latest_metric(name)
        entries = @metrics[name]
        return nil if entries.empty?
        entries.last[:value]
      end

      def best_metric(name, mode: :min)
        entries = @metrics[name]
        return nil if entries.empty?

        if mode == :min
          entries.min_by { |e| e[:value] }[:value]
        else
          entries.max_by { |e| e[:value] }[:value]
        end
      end

      def to_summary
        {
          run_id: @run_id,
          experiment: @experiment_name,
          status: @status,
          duration_s: duration_seconds,
          params: @params,
          latest_metrics: @metrics.transform_values { |v| v.last&.dig(:value) },
          num_artifacts: @artifacts.length,
          tags: @tags
        }
      end

      private

      def generate_run_id
        "run_#{Time.now.utc.strftime('%Y%m%d_%H%M%S')}_#{SecureRandom.hex(4)}" rescue
        "run_#{Time.now.utc.strftime('%Y%m%d_%H%M%S')}_#{rand(0xffff).to_s(16)}"
      end
    end

    class ExperimentTracker
      attr_reader :experiments

      def initialize(storage_dir: "./omni_experiments")
        @storage_dir = storage_dir
        @experiments = Hash.new { |h, k| h[k] = [] }
        @active_runs = {}
      end

      def start_run(experiment_name:, params: {}, tags: {})
        run = ExperimentRun.new(
          experiment_name: experiment_name,
          params: params,
          tags: tags
        )
        @experiments[experiment_name] << run
        @active_runs[run.run_id] = run
        run
      end

      def end_run(run_id, status: :completed)
        run = @active_runs.delete(run_id)
        raise "Run #{run_id} not found" unless run

        case status
        when :completed then run.complete!
        when :failed then run.fail!
        when :cancelled then run.cancel!
        end
        run
      end

      def compare_runs(run_ids, metric_name)
        runs = run_ids.map { |id| find_run(id) }.compact
        return {} if runs.empty?

        comparison = runs.map do |run|
          {
            run_id: run.run_id,
            experiment: run.experiment_name,
            params: run.params,
            best: run.best_metric(metric_name, mode: :min),
            latest: run.latest_metric(metric_name),
            duration_s: run.duration_seconds
          }
        end

        comparison.sort_by { |c| c[:best] || Float::INFINITY }
      end

      def best_run(experiment_name, metric_name, mode: :min)
        runs = @experiments[experiment_name]
        return nil if runs.empty?

        runs.select { |r| r.status == "completed" }
            .min_by { |r| mode == :min ? (r.best_metric(metric_name, mode: :min) || Float::INFINITY) : -(r.best_metric(metric_name, mode: :max) || -Float::INFINITY) }
      end

      def list_experiments
        @experiments.map do |name, runs|
          {
            name: name,
            total_runs: runs.length,
            completed: runs.count { |r| r.status == "completed" },
            failed: runs.count { |r| r.status == "failed" },
            latest_run: runs.last&.to_summary
          }
        end
      end

      def param_diff(run_id_a, run_id_b)
        a = find_run(run_id_a)
        b = find_run(run_id_b)
        return {} unless a && b

        all_keys = (a.params.keys + b.params.keys).uniq
        diff = {}
        all_keys.each do |key|
          va = a.params[key]
          vb = b.params[key]
          diff[key] = { a: va, b: vb } if va != vb
        end
        diff
      end

      private

      def find_run(run_id)
        @active_runs[run_id] ||
          @experiments.values.flatten.find { |r| r.run_id == run_id }
      end
    end
  end
end
