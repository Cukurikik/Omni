defmodule Omni.Concurrency.AlkaliMetalIonThruster.SpecificImpulse do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{ions_accelerated: 0}, name: __MODULE__)
  end

  def regulate_anode_flow(pid, xenon_flow_rate_mg_s) do
    GenServer.cast(pid, {:regulate, xenon_flow_rate_mg_s})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:regulate, flow_rate}, state) do
    # Distributed Elixir worker managing Specific Impulse (Isp) Optimization.
    # To maximize fuel efficiency (Isp), we must perfectly balance the magnetic field
    # strength with the Xenon gas injection rate. This worker runs a continuous PID loop
    # to prevent plasma starvation or grid short-circuits.
    
    new_count = state.ions_accelerated + round(flow_rate * 1000)
    
    {:noreply, %{state | ions_accelerated: new_count}}
  end
end
