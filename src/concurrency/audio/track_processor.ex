defmodule Omni.Concurrency.Audio.TrackProcessor do
  use GenServer
  require Logger

  defmodule Result do
    defsturct [:ok, :error]
    def ok(value), do: %Result{ok: value, error: nil}
    def error(reason), do: %Result{ok: nil, error: reason}
    def is_ok?(%Result{error: nil}), do: true
    def is_ok?(_), do: false
  end

  def start_link(opts) do
    track_id = Keyword.get(opts, :track_id, UUID.uuid4())
    GenServer.start_link(__MODULE__, %{track_id: track_id}, name: via_tuple(track_id))
  end

  defp via_tuple(track_id), do: {:global, {:track_processor, track_id}}

  def process_chunk(track_id, audio_chunk) do
    GenServer.call(via_tuple(track_id), {:process_chunk, audio_chunk})
  end

  @impl true
  def init(state) do
    {:ok, Map.merge(state, %{buffer: [], chunk_count: 0})}
  end

  @impl true
  def handle_call({:process_chunk, audio_chunk}, _from, state) do
    # In production, chunks are routed through the FFI bridging to Python Demucs
    new_count = state.chunk_count + 1
    
    # Store reference to chunk processing task
    task = Task.async(fn -> 
      # Simulate compute delay
      Process.sleep(50)
      {:ok, "processed_#{new_count}"}
    end)

    new_state = %{state | chunk_count: new_count, buffer: [task | state.buffer]}
    {:reply, Result.ok(:enqueued), new_state}
  end

  @impl true
  def handle_info({ref, {:ok, result}}, state) do
    Process.demonitor(ref, [:flush])
    Logger.info("Chunk #{result} completed for track #{state.track_id}")
    
    # Remove task from buffer
    new_buffer = Enum.reject(state.buffer, fn t -> t.ref == ref end)
    {:noreply, %{state | buffer: new_buffer}}
  end

  @impl true
  def handle_info({:DOWN, ref, :process, _pid, reason}, state) do
    Logger.error("Audio chunk task failed: #{inspect(reason)}")
    new_buffer = Enum.reject(state.buffer, fn t -> t.ref == ref end)
    {:noreply, %{state | buffer: new_buffer}}
  end
end
