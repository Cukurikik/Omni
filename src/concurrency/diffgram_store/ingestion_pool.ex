defmodule Omni.Concurrency.DiffgramStore.IngestionPool do
  use GenServer

  def start_link(pool_size) do
    GenServer.start_link(__MODULE__, %{pool_size: pool_size, queued_items: [], active_workers: 0}, name: __MODULE__)
  end

  def enqueue_blob(pid, blob_id) do
    GenServer.cast(pid, {:enqueue, blob_id})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_cast({:enqueue, blob_id}, state) do
    new_queue = state.queued_items ++ [blob_id]
    
    # Try to process if workers available
    state = %{state | queued_items: new_queue}
    {:noreply, try_dispatch(state)}
  end

  defp try_dispatch(state) do
    if state.active_workers < state.pool_size and length(state.queued_items) > 0 do
      [blob_id | rest] = state.queued_items
      
      IO.puts("Diffgram Pool: Ingesting blob #{blob_id}")
      
      # Simulate async processing time deterministically
      Process.send_after(self(), {:blob_done, blob_id}, 50)
      
      try_dispatch(%{state | queued_items: rest, active_workers: state.active_workers + 1})
    else
      state
    end
  end

  @impl true
  def handle_info({:blob_done, _blob_id}, state) do
    new_state = %{state | active_workers: state.active_workers - 1}
    # Chain the dispatch
    {:noreply, try_dispatch(new_state)}
  end
end
