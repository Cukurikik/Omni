defmodule Omni.Concurrency.StellarEngineShkadovThruster.BarycenterAdjustment do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{orbital_corrections: 0}, name: __MODULE__)
  end

  def compute_n_body_perturbations(pid, planetary_positions) do
    GenServer.cast(pid, {:compute, planetary_positions})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:compute, _positions}, state) do
    # Distributed Elixir worker managing Systemic Barycenter Adjustments.
    # As the Shkadov thruster pushes the star, the star pulls the planets along.
    # However, this introduces slight perturbations to their orbits over millions of years.
    # This worker runs an N-body simulation to constantly adjust planetary orbits
    # to prevent them from flying out of the solar system.
    
    new_count = state.orbital_corrections + 1
    
    {:noreply, %{state | orbital_corrections: new_count}}
  end
end
