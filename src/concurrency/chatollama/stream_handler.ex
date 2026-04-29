# OMNI CHATOLLAMA: Stream Handler
# Elixir OTP GenServer for efficiently routing chunked streaming responses 
# from the local Ollama daemon to the connected Web UI clients via WebSockets.
# Source: ollama-webui

defmodule Omni.ChatOllama.StreamHandler do
  use GenServer
  require Logger

  # Client API
  def start_link(client_pid) do
    GenServer.start_link(__MODULE__, %{client: client_pid, buffer: ""})
  end

  def ingest_chunk(pid, chunk) do
    GenServer.cast(pid, {:chunk, chunk})
  end

  def finish_stream(pid) do
    GenServer.cast(pid, :finish)
  end

  # Server Callbacks
  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:chunk, chunk}, state) do
    # In a real scenario, this parses JSON Lines from Ollama
    # `{"model":"llama3","created_at":"...","response":"Hello","done":false}`
    
    try do
      case Jason.decode(chunk) do
        {:ok, %{"response" => token}} ->
          # Push immediately to connected Phoenix Channel / WebSocket
          send(state.client, {:token, token})
          {:noreply, state}
          
        _ -> 
          # Accumulate fragmented JSON chunks if necessary
          new_buffer = state.buffer <> chunk
          {:noreply, %{state | buffer: new_buffer}}
      end
    rescue
      e -> 
        Logger.error("Failed to parse Ollama chunk: #{inspect(e)}")
        {:noreply, state}
    end
  end

  @impl true
  def handle_cast(:finish, state) do
    send(state.client, :stream_complete)
    {:stop, :normal, state}
  end
end
