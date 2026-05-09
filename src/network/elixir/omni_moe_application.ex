defmodule OmniMoE.Application do
  use Application
  # OMNI MOTHER: Elixir App Entry
  def start(_type, _args) do
    OmniMoE.Supervisor.start_link([])
  end
end
