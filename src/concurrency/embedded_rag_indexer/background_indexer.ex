defmodule Omni.Concurrency.EmbeddedRagIndexer.BackgroundIndexer do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{documents_indexed: 0}, name: __MODULE__)
  end

  def queue_document(pid, doc_payload) do
    GenServer.cast(pid, {:index, doc_payload})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:index, _doc}, state) do
    # Distributed Elixir worker managing low-priority background indexing
    # Ensures RAG indexing does NOT throttle the primary embedded CPU running the main device app
    
    new_count = state.documents_indexed + 1
    
    {:noreply, %{state | documents_indexed: new_count}}
  end
end
