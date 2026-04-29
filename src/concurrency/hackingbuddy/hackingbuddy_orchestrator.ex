defmodule HackingBuddy.PentestOrchestrator do
  use GenServer
  @max_targets 50
  def start_link(_), do: GenServer.start_link(__MODULE__, %{targets: %{}, scans: 0}, name: __MODULE__)
  def add_target(id, ip), do: GenServer.call(__MODULE__, {:add, id, ip})
  def run_scan(id), do: GenServer.call(__MODULE__, {:scan, id})
  @impl true
  def init(s), do: {:ok, s}
  @impl true
  def handle_call({:add, id, ip}, _from, s) do
    if map_size(s.targets) >= @max_targets, do: {:reply, {:error, "Target limit"}, s},
    else: {:reply, {:ok, id}, %{s | targets: Map.put(s.targets, id, %{ip: ip, status: :pending})}}
  end
  @impl true
  def handle_call({:scan, id}, _from, s) do
    case Map.get(s.targets, id) do
      nil -> {:reply, {:error, "Target not found"}, s}
      _t -> {:reply, {:ok, :scanning}, %{s | scans: s.scans + 1}}
    end
  end
end
