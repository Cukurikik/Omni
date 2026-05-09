defmodule Omni.ActorSupervisor do
  @moduledoc "OMNI Concurrency Layer: Elixir Fault-Tolerant Supervisor"
  use Supervisor

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      # {Omni.Worker, []}
    ]
    Supervisor.init(children, strategy: :one_for_one)
  end
end
