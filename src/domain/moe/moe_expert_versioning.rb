# moe_expert_versioning.rb — Domain / Operations
# Layer: Domain / Database — Expert Version Control
#
# Experts undergo continuous fine-tuning. This Ruby service interacts with PostgreSQL
# to track expert versions and manage blue/green deployments. It allows the router
# to gracefully bleed traffic from v1.0 to v1.1 without dropping requests.

require 'json'

class ExpertVersioningService
  # Mock database schema
  # CREATE TABLE expert_versions (
  #   id SERIAL, expert_id INT, version VARCHAR(50), 
  #   status VARCHAR(20), deployment_weight FLOAT
  # );

  def initialize
    puts "[Versioning] Initialized Expert Version Control Service."
    # In-memory mock database
    @db = {
      12 => [
        { version: "v1.0", status: "active", weight: 1.0 },
        { version: "v1.1", status: "deploying", weight: 0.0 }
      ]
    }
  end

  def register_new_version(expert_id, new_version_tag)
    @db[expert_id] ||= []
    @db[expert_id] << { version: new_version_tag, status: "standby", weight: 0.0 }
    puts "[Versioning] Registered #{new_version_tag} for Expert #{expert_id} in Standby."
  end

  # Executes a graceful Blue/Green deployment over time
  def shift_traffic(expert_id, from_version, to_version, shift_percentage)
    records = @db[expert_id]
    return unless records

    from_record = records.find { |r| r[:version] == from_version }
    to_record = records.find { |r| r[:version] == to_version }

    return unless from_record && to_record

    # Enforce bounds
    shift = [shift_percentage, from_record[:weight]].min
    
    from_record[:weight] = (from_record[:weight] - shift).round(2)
    to_record[:weight] = (to_record[:weight] + shift).round(2)
    to_record[:status] = "active"

    if from_record[:weight] <= 0.0
      from_record[:status] = "deprecated"
    end

    puts "[Versioning] Expert #{expert_id} Traffic Shift: #{from_version} (#{(from_record[:weight]*100).to_i}%) -> #{to_version} (#{(to_record[:weight]*100).to_i}%)"
    
    # Syncs this weight to the MoE Router in Go via Redis PubSub
    sync_to_router()
  end

  private

  def sync_to_router
    # Mock Redis publish
    # redis.publish("moe:expert:routing_weights", @db.to_json)
  end
end

# Usage:
# v_service = ExpertVersioningService.new
# v_service.shift_traffic(12, "v1.0", "v1.1", 0.25)
