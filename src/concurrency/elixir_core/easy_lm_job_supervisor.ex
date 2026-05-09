defmodule Omni.Concurrency.EasyLMJobSupervisor do
  @moduledoc """
  OMNI Framework - Easy LM Job Supervisor
  Supervises LM training jobs across the Elixir/BEAM nodes.
  """
  use DynamicSupervisor

  def start_link(init_arg) do
    DynamicSupervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    DynamicSupervisor.init(strategy: :one_for_one)
  end

  def start_training_worker(model_name) do
    spec = {Omni.Concurrency.LMWorker, model_name}
    DynamicSupervisor.start_child(__MODULE__, spec)
  end
end
