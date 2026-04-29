defmodule Omni.Concurrency.IpsecVpn.SATracker do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{active_tunnels: %{}}, name: __MODULE__)
  end

  def register_sa(pid, spi, peer_ip) do
    GenServer.cast(pid, {:register, spi, peer_ip})
  end

  def process_packet(pid, spi, size) do
    GenServer.cast(pid, {:packet, spi, size})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:register, spi, peer_ip}, state) do
    new_tunnels = Map.put(state.active_tunnels, spi, %{ip: peer_ip, bytes: 0, pkts: 0})
    {:noreply, %{state | active_tunnels: new_tunnels}}
  end

  @impl true
  def handle_cast({:packet, spi, size}, state) do
    case Map.get(state.active_tunnels, spi) do
      nil ->
        # Drop packet, unknown SPI (Security Parameter Index)
        {:noreply, state}
      tunnel ->
        updated = %{tunnel | bytes: tunnel.bytes + size, pkts: tunnel.pkts + 1}
        new_tunnels = Map.put(state.active_tunnels, spi, updated)
        {:noreply, %{state | active_tunnels: new_tunnels}}
    end
  end
end
