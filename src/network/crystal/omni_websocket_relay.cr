# OMNI Framework - WebSocket Relay (Crystal)
# Extremely fast WebSocket server for streaming LLM completions to clients

require "http/server"

module Omni
  class WebsocketRelay
    @@clients = [] of HTTP::WebSocket

    def self.start(port = 8080)
      ws_handler = HTTP::WebSocketHandler.new do |ws|
        @@clients << ws

        ws.on_message do |message|
          # When receiving a generation request, forward to backend
          # Here we just echo for simulation
          puts "Received prompt: #{message}"
          
          # Simulate token streaming
          spawn do
            ["The", " quick", " brown", " fox", " jumps"].each do |token|
              sleep 0.1
              ws.send({"event" => "token", "data" => token}.to_json)
            end
            ws.send({"event" => "done"}.to_json)
          end
        end

        ws.on_close do
          @@clients.delete(ws)
          puts "Client disconnected"
        end
      end

      server = HTTP::Server.new([ws_handler])
      address = server.bind_tcp("0.0.0.0", port)
      puts "OMNI Crystal WS Relay listening on #{address}"
      server.listen
    end
  end
end

# To run standalone
# Omni::WebsocketRelay.start
