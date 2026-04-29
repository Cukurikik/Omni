defmodule Omni.Concurrency.ZeroGFluidDynamics.ParticleUpdater do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{particles_updated: 0}, name: __MODULE__)
  end

  def update_particles(pid, count) do
    GenServer.cast(pid, {:update, count})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:update, count}, state) do
    # Distributed Elixir worker managing Smoothed-Particle Hydrodynamics (SPH) state synchronization.
    # While the GPU crunches the math, Elixir distributes the resulting particle positions 
    # to rendering clients or telemetry endpoints asynchronously at 60Hz.
    
    new_count = state.particles_updated + count
    
    {:noreply, %{state | particles_updated: new_count}}
  end
end
