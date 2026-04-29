defmodule Omni.Serving.LoadBalancer do
  def get_best_node(nodes) do
    case nodes do
      [] -> {:error, :no_nodes_available}
      _ -> {:ok, Enum.min_by(nodes, fn node -> node.cpu_load end)}
    end
  end

  def route_request(request, nodes) do
    case get_best_node(nodes) do
      {:ok, node} -> {:ok, send_to_node(node, request)}
      error -> error
    end
  end

  defp send_to_node(_node, _request), do: :dispatched
end
