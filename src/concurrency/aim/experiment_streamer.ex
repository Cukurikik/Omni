defmodule Aim.ExperimentStreamer do
  @moduledoc """
  OMNI Engine: Fault-tolerant streamer for Aim experiment metrics.
  """
  use GenServer

  def start_link(experiment_id) do
    GenServer.start_link(__MODULE__, experiment_id, name: via_tuple(experiment_id))
  end

  def init(experiment_id) do
    {:ok, %{experiment_id: experiment_id, metrics: []}}
  end

  def push_metric(pid, name, value, step) do
    GenServer.cast(pid, {:push_metric, name, value, step})
  end

  def handle_cast({:push_metric, name, value, step}, state) do
    metric_point = %{name: name, value: value, step: step, timestamp: System.system_time(:millisecond)}
    # In production: Flush to disk/Kafka when buffer reaches threshold
    new_metrics = [metric_point | state.metrics]
    {:noreply, %{state | metrics: new_metrics}}
  end

  defp via_tuple(experiment_id), do: {:via, Registry, {Aim.Registry, experiment_id}}
end
