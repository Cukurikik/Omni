defmodule Omni.Network.Telemetry do
  @moduledoc """
  OMNI MOTHER: Elixir Telemetry Aggregator (Production Grade)
  High-throughput metric collector utilizing Erlang processes.
  """
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{}, name: __MODULE__)
  end

  def record_metric(metric_name, value) do
    GenServer.cast(__MODULE__, {:record, metric_name, value})
  end

  def init(state) do
    {:ok, state}
  end

  def handle_cast({:record, metric_name, value}, state) do
    new_state = Map.update(state, metric_name, [value], &[value | &1])
    {:noreply, new_state}
  end
end
