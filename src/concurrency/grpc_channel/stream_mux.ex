defmodule Omni.Concurrency.GrpcChannel.StreamMux do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{streams: %{}}, name: __MODULE__)
  end

  def route_frame(pid, stream_id, frame_size) do
    GenServer.cast(pid, {:frame, stream_id, frame_size})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:frame, stream_id, frame_size}, state) do
    current = Map.get(state.streams, stream_id, 0)
    new_streams = Map.put(state.streams, stream_id, current + frame_size)
    
    # IO.puts("gRPC Mux: Routed frame to Stream [#{stream_id}]")
    
    {:noreply, %{state | streams: new_streams}}
  end
end
