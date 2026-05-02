# @omni-domain Concurrency Layer (Pixie)
# @omni-source various/pixie
# @omni-description Pixie Stream Processor mimicking real-time observability pipelines.
# @omni-requirement zero-mock, monadic-error

defmodule Pixie.StreamProcessor do
  @moduledoc """
  Concurrent stream processor for Pixie telemetry data.
  """
  use GenServer

  def start_link(opts \\ []) do
    GenServer.start_link(__MODULE__, :ok, opts)
  end

  def process_event(pid, event) do
    if is_map(event) and Map.has_key?(event, :timestamp) do
      GenServer.call(pid, {:process, event})
    else
      {:error, "Invalid event format"}
    end
  end

  @impl true
  def init(:ok) do
    {:ok, %{processed_count: 0, events: []}}
  end

  @impl true
  def handle_call({:process, event}, _from, state) do
    new_state = %{
      processed_count: state.processed_count + 1,
      events: [event | state.events]
    }
    {:reply, {:ok, new_state.processed_count}, new_state}
  end
end
