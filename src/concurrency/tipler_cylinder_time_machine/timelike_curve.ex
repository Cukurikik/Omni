defmodule Omni.Concurrency.TiplerCylinderTimeMachine.TimelikeCurve do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{temporal_loops_calculated: 0}, name: __MODULE__)
  end

  def compute_past_light_cone_intersection(pid, spacecraft_trajectory) do
    GenServer.cast(pid, {:intersect, spacecraft_trajectory})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:intersect, _trajectory}, state) do
    # Distributed Elixir worker managing Closed Timelike Curve (CTC) Mapping.
    # To travel backwards in time safely, the ship must navigate the incredibly steep
    # gravity well of the spinning cylinder without being crushed by tidal forces,
    # tracing a precise spiral path that dips below its own past light cone.
    
    new_count = state.temporal_loops_calculated + 1
    
    {:noreply, %{state | temporal_loops_calculated: new_count}}
  end
end
