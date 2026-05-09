require "http/server"

module OmniFramework::WebRouter
  server = HTTP::Server.new do |context|
    context.response.content_type = "application/json"
    
    case context.request.path
    when "/api/health"
      context.response.print %({"status": "ok", "layer": "crystal_web"})
    when "/api/infer"
      if context.request.method == "POST"
        context.response.print %({"prediction": "success", "confidence": 0.99})
      else
        context.response.status_code = 405
        context.response.print %({"error": "Method Not Allowed"})
      end
    else
      context.response.status_code = 404
      context.response.print %({"error": "Not Found in OMNI Crystal Router"})
    end
  end

  address = server.bind_tcp "0.0.0.0", 8080
  puts "OMNI Crystal Router listening on http://#{address}"
  # server.listen
end
