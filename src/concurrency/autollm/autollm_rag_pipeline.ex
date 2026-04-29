defmodule AutoLLM.RAGPipeline do
  use GenServer
  @max_docs 100000
  def start_link(_), do: GenServer.start_link(__MODULE__, %{docs: 0, queries: 0}, name: __MODULE__)
  def ingest_doc(title, content), do: GenServer.call(__MODULE__, {:ingest, title, content})
  def query(q), do: GenServer.call(__MODULE__, {:query, q})
  @impl true
  def init(s), do: {:ok, s}
  @impl true
  def handle_call({:ingest, t, c}, _from, s) do
    cond do
      s.docs >= @max_docs -> {:reply, {:error, "Doc limit reached"}, s}
      byte_size(c) > 10_000_000 -> {:reply, {:error, "Content exceeds 10MB"}, s}
      String.length(t) > 512 -> {:reply, {:error, "Title too long"}, s}
      true -> {:reply, {:ok, s.docs + 1}, %{s | docs: s.docs + 1}}
    end
  end
  @impl true
  def handle_call({:query, q}, _from, s) do
    if String.length(q) > 4096, do: {:reply, {:error, "Query exceeds 4KB"}, s},
    else: {:reply, {:ok, :results}, %{s | queries: s.queries + 1}}
  end
end
