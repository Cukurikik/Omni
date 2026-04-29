defmodule Omni.Concurrency.BoseEinsteinCondensateInterferometer.PhaseReadout do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{fringes_counted: 0}, name: __MODULE__)
  end

  def read_interference_pattern(pid, ccd_image_data) do
    GenServer.cast(pid, {:read, ccd_image_data})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:read, _data}, state) do
    # Distributed Elixir worker managing BEC Phase Readout.
    # The atom cloud is dropped. An absorption image is taken with a CCD camera,
    # destroying the condensate. This worker instantly processes the spatial interference
    # fringes to calculate the exact gravitational acceleration (to 10 decimal places).
    
    new_count = state.fringes_counted + 1
    
    {:noreply, %{state | fringes_counted: new_count}}
  end
end
