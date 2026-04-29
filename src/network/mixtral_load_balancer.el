defmodule Omni.Network.MixtralLB do
  def balance_load(nodes, request_id) do
    case length(nodes) do
      0 -> {:error, "No nodes available"}
      n -> {:ok, Enum.at(nodes, rem(request_id, n))}
    end
  end
end
