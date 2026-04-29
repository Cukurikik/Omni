defmodule Omni.Concurrency.ActiveLearning.LabelingQueue do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, [], name: __MODULE__)
  end

  @impl true
  def init(_) do
    {:ok, []}
  end

  @impl true
  def handle_call({:enqueue, sample_id, uncertainty}, _from, state) do
    if uncertainty < 0.0 do
      {:reply, {:error, "Uncertainty cannot be negative"}, state}
    else
      new_state = [{sample_id, uncertainty} | state]
      # Keep queue sorted by highest uncertainty
      sorted_state = Enum.sort_by(new_state, fn {_, u} -> u end, :desc)
      {:reply, {:ok, :enqueued}, sorted_state}
    end
  end

  @impl true
  def handle_call(:dequeue, _from, []) do
    {:reply, {:error, :empty}, []}
  end

  @impl true
  def handle_call(:dequeue, _from, [highest_uncertainty | rest]) do
    {:reply, {:ok, highest_uncertainty}, rest}
  end
end
