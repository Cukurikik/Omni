require 'net/http'
require 'json'

# OMNI MOTHER: Nekos.moe API Bridge (From JSON Repo List)
# Fetches images to act as avatars for Expert Nodes in the Visualizer

module OmniNekosAPI
  class Client
    def initialize
      @base_url = "https://nekos.moe/api/v1/random/image"
    end

    def fetch_expert_avatar
      uri = URI(@base_url)
      response = Net::HTTP.get(uri)
      JSON.parse(response)
    rescue => e
      { "error" => e.message }
    end
  end
end
