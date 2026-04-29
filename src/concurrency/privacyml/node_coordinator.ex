defmodule Omni.Concurrency.PrivacyML.NodeCoordinator do
  use GenServer

  def start_link(opts) do
    GenServer.start_link(__MODULE__, :ok, opts)
  end

  @impl true
  def init(:ok) do
    {:ok, %{nodes: %{}, aggregated_count: 0}}
  end

  @impl true
  def handle_cast({:register_node, node_id, public_key}, state) do
    if Map.has_key?(state.nodes, node_id) do
      {:noreply, state}
    else
      new_nodes = Map.put(state.nodes, node_id, %{key: public_key, status: :active})
      {:noreply, %{state | nodes: new_nodes}}
    end
  end

  @impl true
  def handle_call({:submit_gradients, node_id, _gradients}, _from, state) do
    case Map.fetch(state.nodes, node_id) do
      {:ok, node_info} ->
        if node_info.status == :active do
          # Proceed with mathematical validation of gradients
          new_state = %{state | aggregated_count: state.aggregated_count + 1}
          {:reply, {:ok, "Gradients accepted"}, new_state}
        else
          {:reply, {:error, "Node is inactive"}, state}
        end
      :error ->
        {:reply, {:error, "Node not registered"}, state}
    end
  end
end
