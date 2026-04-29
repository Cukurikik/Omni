defmodule Omni.H2O.Gossip do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def init(_) do
    schedule_gossip()
    {:ok, %{cluster_state: %{}}}
  end

  def handle_info(:gossip_tick, state) do
    # Broadcast cluster health
    schedule_gossip()
    {:noreply, state}
  end

  defp schedule_gossip() do
    Process.send_after(self(), :gossip_tick, 1000)
  end
end
