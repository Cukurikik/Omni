defmodule Omni.Concurrency.QuicTransport.CidRouter do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{connections: %{}}, name: __MODULE__)
  end

  def route_packet(pid, cid, packet_size) do
    GenServer.cast(pid, {:route, cid, packet_size})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:route, cid, packet_size}, state) do
    # QUIC Connection ID (CID) routing allows connection migration (e.g. WiFi to LTE)
    # without tearing down the connection, unlike TCP.
    
    current = Map.get(state.connections, cid, 0)
    new_conns = Map.put(state.connections, cid, current + packet_size)
    
    {:noreply, %{state | connections: new_conns}}
  end
end
