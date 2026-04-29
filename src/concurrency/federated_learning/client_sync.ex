defmodule Omni.Concurrency.FederatedLearning.ClientSync do
  use GenServer

  def start_link(_) do
    GenServer.start_link(__MODULE__, %{clients: %{}, round: 0, required_clients: 5}, name: __MODULE__)
  end

  def register_client(pid, client_id) do
    GenServer.call(pid, {:register, client_id})
  end

  def submit_weights(pid, client_id, weights_ref) do
    GenServer.cast(pid, {:submit, client_id, weights_ref})
  end

  @impl true
  def init(state) do
    {:ok, state}
  end

  @impl true
  def handle_call({:register, client_id}, _from, state) do
    if Map.has_key?(state.clients, client_id) do
      {:reply, {:error, "Client already registered"}, state}
    else
      new_clients = Map.put(state.clients, client_id, %{status: :idle, weights: nil})
      {:reply, {:ok, "Registered"}, %{state | clients: new_clients}}
    end
  end

  @impl true
  def handle_cast({:submit, client_id, weights_ref}, state) do
    if Map.has_key?(state.clients, client_id) do
      updated_client = %{state.clients[client_id] | status: :submitted, weights: weights_ref}
      new_clients = Map.put(state.clients, client_id, updated_client)
      
      # Check if round is complete deterministically
      submitted_count = Enum.count(new_clients, fn {_, v} -> v.status == :submitted end)
      
      if submitted_count >= state.required_clients do
        # Proceed to aggregation pipeline
        IO.puts("Round #{state.round} Complete! Triggering FedAvg.")
        
        # Reset for next round
        reset_clients = Map.new(new_clients, fn {k, _} -> {k, %{status: :idle, weights: nil}} end)
        {:noreply, %{state | clients: reset_clients, round: state.round + 1}}
      else
        {:noreply, %{state | clients: new_clients}}
      end
    else
      {:noreply, state}
    end
  end
end
