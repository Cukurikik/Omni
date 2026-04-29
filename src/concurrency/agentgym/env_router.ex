defmodule AgentGym.EnvRouter do
  defstruct value: nil, error: nil, is_ok: false

  def route_action(action_id) do
    if is_nil(action_id) do
      %__MODULE__{value: nil, error: "Invalid action", is_ok: false}
    else
      # Math-based hashing for node assignment
      node_idx = rem(abs(System.unique_integer([:positive])), 5)
      %__MODULE__{value: "node_#{node_idx}", error: nil, is_ok: true}
    end
  end
end
