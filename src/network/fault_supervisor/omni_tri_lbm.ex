# omni_tri_lbm.ex — Large Behavioral Model Supervisor
# Inspired by: TRI-LBM (Large Behavioral Model for Dexterous Manipulation)
# Layer: Network - Concurrency / Elixir
#
# OTP Supervisor and GenServer for managing robotic behavioral models,
# handling state telemetry, and broadcasting policy actions across the network.

defmodule Omni.Robotics.LBMSupervisor do
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      {Omni.Robotics.TelemetryReceiver, []},
      {Omni.Robotics.BehavioralInferenceWorker, [name: :lbm_worker_1]},
      {Omni.Robotics.BehavioralInferenceWorker, [name: :lbm_worker_2]},
      {Omni.Robotics.ActionBroadcaster, []}
    ]

    # One for One strategy: if an inference worker crashes, only that worker restarts
    Supervisor.init(children, strategy: :one_for_one)
  end
end

defmodule Omni.Robotics.BehavioralInferenceWorker do
  use GenServer
  require Logger

  @doc """
  Starts the Inference Worker.
  """
  def start_link(opts) do
    name = Keyword.get(opts, :name, __MODULE__)
    GenServer.start_link(__MODULE__, opts, name: name)
  end

  @doc """
  Request an action based on current state observations.
  """
  def get_action(pid, observation) do
    GenServer.call(pid, {:infer_action, observation}, 5000)
  end

  @impl true
  def init(opts) do
    Logger.info("Starting BehavioralInferenceWorker: #{inspect(opts[:name])}")
    
    # Initialize connection to local Rust/C++ inference runtime bridge
    # state represents the context window buffer
    {:ok, %{context_buffer: [], max_len: 128}}
  end

  @impl true
  def handle_call({:infer_action, observation}, _from, state) do
    # Append to sliding window
    new_buffer = [observation | state.context_buffer] |> Enum.take(state.max_len)
    
    # Call to underlying compute layer (e.g. via NIF or Port)
    # Mocked for the OTP structure manifestation
    action = compute_policy(new_buffer)
    
    new_state = %{state | context_buffer: new_buffer}
    {:reply, {:ok, action}, new_state}
  end

  defp compute_policy(_context) do
    # Represents the diffusion-based or autoregressive action generation
    %{
      "gripper_pose" => [0.1, -0.2, 0.5, 1.0, 0.0, 0.0, 0.0],
      "gripper_open" => 0.0,
      "confidence" => 0.95
    }
  end
end
