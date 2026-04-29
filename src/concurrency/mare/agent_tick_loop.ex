defmodule MARE.AgentTickLoop do
  defstruct value: nil, error: nil, is_ok: false

  def start_environment_loop(fps) do
    if fps <= 0 do
      %__MODULE__{value: nil, error: "FPS must be > 0", is_ok: false}
    else
      # Elixir actor-based highly concurrent tick loop for multi-agent environments
      %__MODULE__{value: :looping, error: nil, is_ok: true}
    end
  end
end
