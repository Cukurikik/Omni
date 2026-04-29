defmodule Omni.Concurrency.MolecularMPNN.BatchLoader do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{queue: [], processing: false}, name: __MODULE__)
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:load_batch, batch_data}, _from, state) do
    if length(batch_data) == 0 do
      {:reply, {:error, "Empty batch"}, state}
    else
      new_queue = state.queue ++ batch_data
      {:reply, {:ok, :queued, length(new_queue)}, %{state | queue: new_queue}}
    end
  end

  @impl true
  def handle_call(:process_next, _from, %{queue: []} = state) do
    {:reply, {:error, :empty}, state}
  end

  @impl true
  def handle_call(:process_next, _from, %{queue: [next_batch | rest]} = state) do
    # Deterministic batch dispatch
    {:reply, {:ok, next_batch}, %{state | queue: rest}}
  end
end
