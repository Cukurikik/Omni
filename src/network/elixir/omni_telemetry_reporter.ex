# OMNI Network — Elixir Telemetry Reporter
# Worker node for the Erlang supervision tree

defmodule OmniTelemetryReporter do
  use GenServer
  require Logger

  def start_link(_opts \\ []) do
    GenServer.start_link(__MODULE__, :ok, name: __MODULE__)
  end

  @impl true
  def init(:ok) do
    Logger.info("OMNI Telemetry Reporter Started")
    schedule_report()
    {:ok, %{metrics_sent: 0}}
  end

  @impl true
  def handle_info(:report, state) do
    # Collect VM metrics
    memory = :erlang.memory(:total)
    processes = length(:erlang.processes())
    
    Logger.debug("Telemetry -> Mem: #{memory} bytes, Procs: #{processes}")
    
    # Simulate sending to InfluxDB or Kafka
    schedule_report()
    {:noreply, %{state | metrics_sent: state.metrics_sent + 1}}
  end

  defp schedule_report do
    Process.send_after(self(), :report, 5000) # Report every 5 seconds
  end
end
