# OmniActorSupervisor - OMNI Concurrency Layer
#
# Utilizes Elixir's OTP Actor Model for absolute fault tolerance.
# Implements a dynamic supervisor for managing isolated inference workers.

defmodule Omni.Network.ElixirCore.OmniActorSupervisor do
  use DynamicSupervisor

  @doc """
  Starts the Omni Actor Supervisor.
  """
  def start_link(init_arg) do
    DynamicSupervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    # MaxRestarts limits failure cascades
    DynamicSupervisor.init(
      strategy: :one_for_one,
      max_restarts: 10,
      max_seconds: 5
    )
  end

  @doc """
  Spawns an isolated worker process. Strictly returns monadic tuple.
  """
  def spawn_inference_worker(worker_args) do
    spec = {Omni.Network.ElixirCore.InferenceWorker, worker_args}
    
    case DynamicSupervisor.start_child(__MODULE__, spec) do
      {:ok, pid} -> {:ok, pid}
      {:error, reason} -> {:error, reason}
    end
  end
  
  @doc """
  Forcefully terminates an unresponsive actor.
  """
  def terminate_worker(pid) do
    case DynamicSupervisor.terminate_child(__MODULE__, pid) do
      :ok -> {:ok, :terminated}
      {:error, reason} -> {:error, reason}
    end
  end
end
