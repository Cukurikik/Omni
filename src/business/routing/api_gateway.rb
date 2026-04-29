require 'sinatra/base'
require 'json'

module OmniFramework
  class APIGateway < Sinatra::Base
    set :show_exceptions, false

    error do
      content_type :json
      status 500
      { error: "Omni Gateway Error: #{env['sinatra.error'].message}" }.to_json
    end

    before do
      content_type :json
      # Monadic check for auth token
      token = request.env['HTTP_AUTHORIZATION']
      halt 401, { error: "Missing authorization" }.to_json unless token == 'Bearer omni-secure-token'
    end

    post '/api/v1/dispatch' do
      payload = JSON.parse(request.body.read)
      if payload['task_id'].nil?
        halt 400, { error: "Missing task_id" }.to_json
      end
      
      # Mocking dispatch to actual Omni Go Kernel
      { status: "Dispatched", task_id: payload['task_id'] }.to_json
    end
  end
end
