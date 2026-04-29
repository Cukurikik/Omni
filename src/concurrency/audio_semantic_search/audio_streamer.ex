defmodule Omni.Concurrency.AudioSemanticSearch.AudioStreamer do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{streams_active: 0}, name: __MODULE__)
  end

  def ingest_audio_chunk(pid, chunk_data) do
    GenServer.call(pid, {:ingest, chunk_data})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:ingest, _chunk}, _from, state) do
    # Distributed Elixir worker managing continuous infinite streams of audio
    # Useful for live Audio RAG applications (e.g. summarizing a live 3-hour podcast)
    
    new_count = state.streams_active + 1
    
    {:reply, :ok, %{state | streams_active: new_count}}
  end
end
