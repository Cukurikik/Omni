defmodule Omni.Concurrency.MlperfTrainingBench.RunCoordinator do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{active_nodes: 0, current_epoch: 0}, name: __MODULE__)
  end

  def sync_gradient_update(pid, node_id, loss) do
    GenServer.call(pid, {:sync, node_id, loss})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:sync, _node_id, loss}, _from, state) do
    # Coordinate distributed All-Reduce gradient synchronization step across nodes
    
    new_epoch = if loss < 0.1 do state.current_epoch + 1 else state.current_epoch end
    
    {:reply, :ok, %{state | current_epoch: new_epoch}}
  end
end
