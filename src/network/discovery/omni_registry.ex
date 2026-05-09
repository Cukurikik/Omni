# omni_registry.ex — Distributed Service Registry
# Layer: Network / Elixir
#
# Utilizes Elixir's Registry to track and route messages dynamically 
# to inference workers distributed across the OMNI cluster.

defmodule Omni.Network.Registry do
  @moduledoc """
  A local/distributed registry mapping model names and task IDs 
  to the specific GenServer PIDs handling the compute workload.
  """

  # Start the standard Elixir Registry
  def child_spec(_opts) do
    Registry.child_spec(
      keys: :unique,
      name: __MODULE__,
      partitions: System.schedulers_online()
    )
  end

  @doc """
  Registers the current process as the handler for a specific model or task.
  """
  def register_worker(model_name) do
    case Registry.register(__MODULE__, model_name, %{status: :active}) do
      {:ok, _} -> :ok
      {:error, {:already_registered, _pid}} -> {:error, :already_exists}
    end
  end

  @doc """
  Looks up the PID of a worker handling the given model.
  Returns `{:ok, pid}` or `{:error, :not_found}`.
  """
  def lookup_worker(model_name) do
    case Registry.lookup(__MODULE__, model_name) do
      [{pid, _value}] -> {:ok, pid}
      [] -> {:error, :not_found}
    end
  end

  @doc """
  Unregisters the process from the registry.
  """
  def unregister_worker(model_name) do
    Registry.unregister(__MODULE__, model_name)
  end
end
