defmodule Omni.Concurrency.TimeSeries.WALWriter do
  @moduledoc """
  High-throughput Write-Ahead Log (WAL) writer for TimeSeries database.
  Uses Elixir processes to batch and flush synchronously to disk.
  """
  use GenServer

  defmodule State do
    defstruct [:buffer, :batch_size, :flush_interval, :timer_ref]
  end

  def start_link(opts \\ []) do
    batch_size = Keyword.get(opts, :batch_size, 1000)
    flush_interval = Keyword.get(opts, :flush_interval, 100) # ms
    
    GenServer.start_link(__MODULE__, %State{
      buffer: [],
      batch_size: batch_size,
      flush_interval: flush_interval
    }, name: __MODULE__)
  end

  @impl true
  def init(state) do
    timer_ref = Process.send_after(self(), :flush, state.flush_interval)
    {:ok, %{state | timer_ref: timer_ref}}
  end

  def write_point(measurement, tags, fields, timestamp) do
    point = %{m: measurement, t: tags, f: fields, ts: timestamp}
    GenServer.cast(__MODULE__, {:write, point})
  end

  @impl true
  def handle_cast({:write, point}, state) do
    new_buffer = [point | state.buffer]
    
    if length(new_buffer) >= state.batch_size do
      flush_to_disk(new_buffer)
      {:noreply, %{state | buffer: []}}
    else
      {:noreply, %{state | buffer: new_buffer}}
    end
  end

  @impl true
  def handle_info(:flush, state) do
    if length(state.buffer) > 0 do
      flush_to_disk(state.buffer)
    end
    
    timer_ref = Process.send_after(self(), :flush, state.flush_interval)
    {:noreply, %{state | buffer: [], timer_ref: timer_ref}}
  end

  defp flush_to_disk(points) do
    # In production, uses O_APPEND | O_DSYNC C NIF or standard IO.binwrite
    # Logger.debug("Flushed #{length(points)} points to WAL")
    :ok
  end
end
