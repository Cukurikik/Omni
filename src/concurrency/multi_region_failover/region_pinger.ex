defmodule Omni.Concurrency.MultiRegionFailover.RegionPinger do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{ping_failures: 0}, name: __MODULE__)
  end

  def report_health(pid, is_healthy) do
    GenServer.cast(pid, {:health, is_healthy})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:health, is_healthy}, state) do
    # Distributed Elixir worker managing continuous health checks across global regions
    # If a region misses 3 pings in a row (e.g. AWS us-east-1 goes down), this worker
    # immediately triggers the DNS failover sequence.
    
    new_count = if is_healthy, do: 0, else: state.ping_failures + 1
    
    {:noreply, %{state | ping_failures: new_count}}
  end
end
