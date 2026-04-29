defmodule Omni.Semester14.Batch8.AwesomeLLM4SE.Pool do
  @moduledoc """
  Bounded Elixir Actor Pool for AwesomeLLM4SE concurrent document indexing.
  """
  use GenServer

  @max_pool_size 50

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{active: 0, queue: []}, name: __MODULE__)
  end

  def submit_document(doc_id, text) do
    GenServer.call(__MODULE__, {:submit, doc_id, text})
  end

  # Callbacks

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:submit, doc_id, text}, _from, state) do
    if state.active >= @max_pool_size do
      # Monadic error mapped to Elixir tuple convention
      {:reply, {:error, "OMNI_LIMIT: Max indexing workers reached."}, state}
    else
      # Spawn linked worker process to handle parsing
      Task.start_link(fn -> process_document(doc_id, text) end)
      {:reply, {:ok, :processing}, %{state | active: state.active + 1}}
    end
  end

  @impl true
  def handle_info({:DOWN, _ref, :process, _pid, _reason}, state) do
    # Worker finished
    {:noreply, %{state | active: max(0, state.active - 1)}}
  end

  defp process_document(_doc_id, text) do
    # Simulate processing time
    Process.sleep(100)
    # Output goes to R clustering layer via OMNI bridge
  end
end
