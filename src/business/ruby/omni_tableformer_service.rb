# OMNI Framework - Ruby Service Wrapper for TableFormer Encoding

require 'net/http'
require 'json'
require 'uri'

module OmniFramework
  class TableformerService
    def initialize
      @api_endpoint = URI("http://omni-erlang-gateway:8085/api/v1/encode_table")
    end

    def encode_table(table_data, text_query)
      raise ArgumentError, "OMNI: Table data cannot be empty" if table_data.nil? || table_data.empty?

      payload = {
        table: table_data,
        query: text_query
      }.to_json

      begin
        response = Net::HTTP.post(@api_endpoint, payload, "Content-Type" => "application/json")
        
        if response.is_a?(Net::HTTPSuccess)
          JSON.parse(response.body)
        else
          { error: "OMNI TableFormer Service failed with status #{response.code}" }
        end
      rescue StandardError => e
        { error: "OMNI TableFormer Connection Error: #{e.message}" }
      end
    end
  end
end
