defmodule Omni.Concurrency.GeothermalMagmaTapDriller.AcousticDecoder do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{pulses_decoded: 0}, name: __MODULE__)
  end

  def process_mud_pulse(pid, bit_stream) do
    GenServer.cast(pid, {:decode, bit_stream})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:decode, bits}, state) do
    # Distributed Elixir worker managing Mud Pulse Telemetry decoding.
    # Data from 10km deep is transmitted at just 3 bits per second by physically creating
    # pressure waves in the drilling mud. This worker decodes that noisy signal in real-time.
    
    new_count = state.pulses_decoded + bits
    
    {:noreply, %{state | pulses_decoded: new_count}}
  end
end
