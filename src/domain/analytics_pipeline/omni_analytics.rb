# OMNI Analytics Pipeline Engine
# Domain Layer
# Rapid DSL for formatting telemetry and compute mathematical metrics into business intelligence reports.

class OmniAnalyticsEngine
  attr_reader :reports_generated, :data_points_processed

  def initialize
    @reports_generated = 0
    @data_points_processed = 0
    @buffer = []
  end

  # Monadic-like error handling in Ruby
  def ingest_telemetry(metric_name, value, timestamp)
    return { ok: false, error: "AnalyticsError: Invalid metric name" } if metric_name.nil? || metric_name.empty?
    return { ok: false, error: "AnalyticsError: Value must be numeric" } unless value.is_a?(Numeric)

    @buffer << { metric: metric_name, value: value, ts: timestamp }
    @data_points_processed += 1

    { ok: true }
  end

  def generate_quarterly_aggregate
    return { ok: false, error: "AnalyticsError: Buffer empty" } if @buffer.empty?

    # Standard statistical aggregations without mocking databases
    aggregate = Hash.new { |h, k| h[k] = { sum: 0.0, count: 0, min: Float::INFINITY, max: -Float::INFINITY } }

    @buffer.each do |entry|
      metric = entry[:metric]
      val = entry[:value]

      aggregate[metric][:sum] += val
      aggregate[metric][:count] += 1
      aggregate[metric][:min] = val if val < aggregate[metric][:min]
      aggregate[metric][:max] = val if val > aggregate[metric][:max]
    end

    report = {}
    aggregate.each do |k, v|
      report[k] = {
        average: v[:sum] / v[:count],
        min: v[:min],
        max: v[:max],
        total_data_points: v[:count]
      }
    end

    @buffer.clear # Free memory after generation
    @reports_generated += 1

    { ok: true, report: report }
  end

  def diagnostics
    {
      engine: "OmniAnalyticsEngine",
      points_processed: @data_points_processed,
      reports_created: @reports_generated,
      memory_buffer_size: @buffer.size,
      status: "Operational"
    }
  end
end
