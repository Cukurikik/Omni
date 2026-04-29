require 'sinatra/base'
require 'json'

class InferenceGateway < Sinatra::Base
  post '/predict' do
    content_type :json
    payload = JSON.parse(request.body.read)
    
    if payload['features'].nil?
      halt 400, { error: "Missing features" }.to_json
    end
    
    { status: "success", prediction: 0.84 }.to_json
  end
end
