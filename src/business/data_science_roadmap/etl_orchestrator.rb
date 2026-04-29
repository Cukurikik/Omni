# OMNI DATA SCIENCE ROADMAP: ETL Orchestrator
# Ruby DSL for defining Data Engineering ETL (Extract, Transform, Load) workflows.
# Source: Moataz-Elmesmary/Data-Science-Roadmap

module Omni
  module ETL
    class WorkflowError < StandardError; end

    class Orchestrator
      attr_reader :workflow_name, :steps

      def initialize(workflow_name)
        @workflow_name = workflow_name
        @steps = []
        @state = {}
      end

      # DSL methods
      def extract(source_name, &block)
        raise WorkflowError, "Extract step already defined." if @steps.any? { |s| s[:type] == :extract }
        @steps << { type: :extract, name: source_name, action: block }
      end

      def transform(transformation_name, &block)
        @steps << { type: :transform, name: transformation_name, action: block }
      end

      def load(destination_name, &block)
        raise WorkflowError, "Load step already defined." if @steps.any? { |s| s[:type] == :load }
        @steps << { type: :load, name: destination_name, action: block }
      end

      # Execution logic
      def execute!
        puts "Starting ETL Workflow: #{@workflow_name}"
        
        begin
          @steps.each do |step|
            puts "[#{step[:type].to_s.upcase}] Executing: #{step[:name]}"
            
            # Execute block within the context of the state
            result = step[:action].call(@state)
            
            if step[:type] == :extract
               @state[:raw_data] = result
            elsif step[:type] == :transform
               @state[:transformed_data] = result
            end
          end
          
          puts "Workflow #{@workflow_name} completed successfully."
          true
        rescue StandardError => e
          puts "Workflow Error: #{e.message}"
          false
        end
      end
    end
  end
end

# Usage example (Internal to the system)
# pipeline = Omni::ETL::Orchestrator.new("Daily_Sales_Sync")
# pipeline.extract("S3_Bucket") { |state| "raw_csv_data" }
# pipeline.transform("Clean_Nulls") { |state| state[:raw_data].upcase }
# pipeline.load("PostgreSQL") { |state| puts "Saving #{state[:transformed_data]}" }
# pipeline.execute!
