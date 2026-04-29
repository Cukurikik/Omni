# Omni SubgraphRAG Actor (Elixir)
defmodule Omni.SubgraphRAG do
  def extract_subgraph(adj, seeds, max_hops) do
    do_extract(adj, MapSet.new(seeds), seeds, [], max_hops)
  end
  defp do_extract(_adj, _visited, _frontier, triples, 0), do: triples
  defp do_extract(adj, visited, frontier, triples, hops) do
    {new_triples, new_frontier, new_visited} =
      Enum.reduce(frontier, {triples, [], visited}, fn node, {ts, nf, vis} ->
        neighbors = Map.get(adj, node, [])
        Enum.reduce(neighbors, {ts, nf, vis}, fn {rel, neighbor}, {t, f, v} ->
          t2 = [{node, rel, neighbor} | t]
          if MapSet.member?(v, neighbor), do: {t2, f, v}, else: {t2, [neighbor | f], MapSet.put(v, neighbor)}
        end)
      end)
    do_extract(adj, new_visited, new_frontier, new_triples, hops - 1)
  end
end
