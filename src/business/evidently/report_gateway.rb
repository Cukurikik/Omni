require 'json'
require 'net/http'

module Omni
  class EvidentlyGateway
    def self.generate_report(dataset_id)
      # Trigger Python Evidently Engine
      uri = URI("http://localhost:5000/evidently/report")
      res = Net::HTTP.post_form(uri, 'dataset' => dataset_id)
      JSON.parse(res.body)
    rescue => e
      { status: 'error', message: e.message }
    end
  end
end
