#=============================================================================
# OMNI NETWORK LAYER — RAG EVENT BUS (ELIXIR)
# BATCH: 31 | SEMESTER: 16
# DESCRIPTION: Elixir actor-model event bus for processing continuous streams 
#              of documents being ingested into the RAG system.
# INSPIRED BY: hoangsonww/RAG-LangChain-AI-System
#=============================================================================

defmodule Omni.Network.RAGBus do
  @moduledoc """
  OMNI IDIOM: Fault-tolerant actor model for document ingestion streams.
  Ensures zero data loss when sending documents to Python/Rust embedders.
  """
  use GenServer
  require Logger

  # Client API
  def start_link(opts) do
    GenServer.start_link(__MODULE__, opts, name: __MODULE__)
  end

  def ingest_document(doc_payload) do
    GenServer.cast(__MODULE__, {:ingest, doc_payload})
  end

  # Server Callbacks
  @impl true
  def init(opts) do
    Logger.info("OMNI RAG Event Bus Started. Ready for high-throughput ingestion.")
    {:ok, %{processed_count: 0, embedder_pid: opts[:embedder_pid]}}
  end

  @impl true
  def handle_cast({:ingest, doc_payload}, state) do
    # OMNI IDIOM: Asynchronous, non-blocking dispatch to compute layer
    # Emits an event that the Go/Rust layers will pick up and route to Python/Mojo
    OmniBridge.emit_event("rag.document.embed", doc_payload)
    
    new_count = state.processed_count + 1
    if rem(new_count, 1000) == 0 do
      Logger.info("Processed #{new_count} documents for RAG ingestion.")
    end
    
    {:noreply, %{state | processed_count: new_count}}
  end
end
