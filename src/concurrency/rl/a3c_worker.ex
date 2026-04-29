# OMNI RL: A3C Worker
# Elixir OTP GenServer representing an asynchronous actor in the A3C algorithm.
# Agents independently interact with the environment and compute gradients, sending them to the global network.
# Source: rlcode/reinforcement-learning

defmodule Omni.RL.A3CWorker do
  use GenServer
  require Logger

  # Client API
  def start_link(worker_id) do
    GenServer.start_link(__MODULE__, %{id: worker_id, step: 0}, name: via_tuple(worker_id))
  end

  def trigger_episode(worker_id) do
    GenServer.cast(via_tuple(worker_id), :run_episode)
  end

  defp via_tuple(worker_id) do
    {:via, Registry, {Omni.RL.WorkerRegistry, worker_id}}
  end

  # Server Callbacks
  @impl true
  def init(state) do
    Logger.info("A3C Worker #{state.id} initialized.")
    {:ok, state}
  end

  @impl true
  def handle_cast(:run_episode, state) do
    # 1. Sync weights from Global Network (simulated)
    # global_weights = Omni.RL.GlobalNet.get_weights()
    
    # 2. Interact with Environment to collect trajectory
    trajectory = simulate_environment_interaction()
    
    # 3. Compute local gradients (simulated)
    gradients = compute_gradients(trajectory)
    
    # 4. Push gradients asynchronously to Global Network
    # Omni.RL.GlobalNet.apply_gradients(gradients)
    
    Logger.info("Worker #{state.id} finished episode. Pushed gradients.")
    {:noreply, %{state | step: state.step + 1}}
  end

  # Internal logic simulations
  defp simulate_environment_interaction do
    # Generates [state, action, reward, next_state]
    Process.sleep(50) # Simulate computation time
    [%{reward: 1.0}]
  end

  defp compute_gradients(_trajectory) do
    # Backpropagation would occur here via NIF to libtorch
    %{policy_grad: 0.1, value_grad: 0.05}
  end
end
