defmodule Omni.Concurrency.MaestStreamWorker do
  @moduledoc """
  OMNI Framework - MAEST Stream Worker
  Processes continuous audio streams for real-time music analysis via GenServer.
  """
  use GenServer

  # Client API
  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def process_chunk(pid, audio_chunk) do
    GenServer.cast(pid, {:process_chunk, audio_chunk})
  end

  def get_analysis_state(pid) do
    GenServer.call(pid, :get_state)
  end

  # Server Callbacks
  @impl true
  def init(_opts) do
    {:ok, %{processed_chunks: 0, last_tags: []}}
  end

  @impl true
  def handle_cast({:process_chunk, _chunk}, state) do
    # In a real pipeline, this delegates to Python/Rust layer
    new_state = %{
      processed_chunks: state.processed_chunks + 1,
      last_tags: ["electronic", "synthwave"]
    }
    {:noreply, new_state}
  end

  @impl true
  def handle_call(:get_state, _from, state) do
    {:reply, {:ok, state}, state}
  end
end
