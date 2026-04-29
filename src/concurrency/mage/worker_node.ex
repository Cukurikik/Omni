defmodule Omni.Mage.WorkerNode do
  use GenServer

  def start_link(node_id) do
    GenServer.start_link(__MODULE__, node_id, name: via_tuple(node_id))
  end

  def init(node_id) do
    {:ok, %{id: node_id, status: :idle, tasks_processed: 0}}
  end

  def handle_cast({:execute_task, task_payload}, state) do
    # Pure mathematical processing
    new_state = %{state | status: :busy}
    _result = process_data(task_payload)
    {:noreply, %{new_state | status: :idle, tasks_processed: state.tasks_processed + 1}}
  end

  defp process_data(payload) do
    # Deterministic task evaluation
    Enum.sum(payload) * 2
  end

  defp via_tuple(node_id), do: {:via, Registry, {Omni.WorkerRegistry, node_id}}
end
