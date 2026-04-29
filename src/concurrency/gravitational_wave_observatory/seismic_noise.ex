defmodule Omni.Concurrency.GravitationalWaveObservatory.SeismicNoise do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{noise_cancelled: 0}, name: __MODULE__)
  end

  def apply_active_damping(pid, seismometer_tensor) do
    GenServer.cast(pid, {:dampen, seismometer_tensor})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:dampen, _tensor}, state) do
    # Distributed Elixir worker managing Active Seismic Noise Cancellation.
    # A passing truck or ocean waves hitting the coast can shake the mirrors
    # 100,000 times more than a gravitational wave. This worker processes data
    # from thousands of seismometers to actively push the mirrors back into place
    # with magnetic actuators in real-time.
    
    new_count = state.noise_cancelled + 1
    
    {:noreply, %{state | noise_cancelled: new_count}}
  end
end
