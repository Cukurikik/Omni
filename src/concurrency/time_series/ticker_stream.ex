defmodule Omni.Concurrency.TimeSeries.TickerStream do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{subscribers: []}, name: __MODULE__)
  end

  @impl true
  def init(state) do
    # Start deterministic simulated data loop
    Process.send_after(self(), :tick, 1000)
    {:ok, state}
  end

  @impl true
  def handle_cast({:subscribe, pid}, state) do
    {:noreply, %{state | subscribers: [pid | state.subscribers]}}
  end

  @impl true
  def handle_info(:tick, state) do
    # Deterministic sine-wave + drift data generation
    time_sec = :os.system_time(:seconds)
    drift = time_sec |> rem(100) |> Kernel./(10)
    value = 100.0 + (10 * :math.sin(time_sec)) + drift

    data = %{
      timestamp: time_sec,
      value: Float.round(value, 2)
    }

    Enum.each(state.subscribers, fn pid -> 
      send(pid, {:ts_data, data}) 
    end)

    Process.send_after(self(), :tick, 1000)
    {:noreply, state}
  end
end
