# moe_elixir_actor_supervisor.ex — Network / Resiliency
# Layer: Network / Erlang VM — Actor Model Supervisor
#
# The Erlang/Elixir BEAM VM is legendary for fault tolerance ("Let it crash").
# This Elixir module implements a Supervisor tree for the MoE distributed nodes.
# If an Expert Node process dies unexpectedly, the Supervisor automatically
# restarts it in a clean state, ensuring 99.999% uptime for the cluster.

defmodule Omni.MoE.ExpertSupervisor do
  use Supervisor
  require Logger

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    Logger.info("[Elixir Supervisor] Initializing MoE Fault-Tolerant Actor Tree.")

    # Define the children (The MoE Expert Worker Actors)
    # In a real cluster, these would be distributed across physical machines
    children = [
      %{
        id: ExpertWorker1,
        start: {Omni.MoE.Worker, :start_link, [[expert_id: 1, port: 9001]]},
        restart: :permanent # Always restart if it crashes
      },
      %{
        id: ExpertWorker2,
        start: {Omni.MoE.Worker, :start_link, [[expert_id: 2, port: 9002]]},
        restart: :permanent
      }
    ]

    # Strategy: one_for_one means if a worker dies, only that worker is restarted
    Supervisor.init(children, strategy: :one_for_one, max_restarts: 10, max_seconds: 60)
  end
end

# Mock Worker Actor
defmodule Omni.MoE.Worker do
  use GenServer
  require Logger

  def start_link(args) do
    GenServer.start_link(__MODULE__, args)
  end

  @impl true
  def init(args) do
    expert_id = Keyword.get(args, :expert_id)
    Logger.info("[Elixir Worker] Expert #{expert_id} started.")
    {:ok, %{id: expert_id, status: :ready}}
  end
  
  # Handle an incoming tensor processing request
  @impl true
  def handle_cast({:process_tensor, _tensor_data}, state) do
    # Simulate work
    # ...
    # Simulate a random crash to test the supervisor
    if :rand.uniform(100) > 98 do
      Logger.error("[Elixir Worker] Expert #{state.id} CRASHED!")
      raise "Simulated OOM or Hardware Failure"
    end
    
    {:noreply, state}
  end
end
