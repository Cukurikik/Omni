defmodule OmniMoE.Supervisor do
  use Supervisor

  # OMNI MOTHER: Elixir Fault-Tolerant Supervisor
  # Monitors the Erlang-based Expert Actors

  def start_link(init_arg) do
    Supervisor.start_link(__MODULE__, init_arg, name: __MODULE__)
  end

  @impl true
  def init(_init_arg) do
    children = [
      {OmniMoE.ExpertActor, name: :expert_1},
      {OmniMoE.ExpertActor, name: :expert_2}
    ]

    Supervisor.init(children, strategy: :one_for_one)
  end
end
